"""Genera resultados agregados a partir del extracto de Aprendia para Power BI."""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path

import pandas as pd


TABLAS = {
    'plan': ('Id_plan', 'Nombre'),
    'Usuario': ('Id_usuario', 'Rol'),
    'Curso': ('Id_curso', 'Profesor_id', 'Categoria', 'Publicado'),
    'Modulo': ('Id_modulo', 'Curso_id'),
    'Leccion': ('Id_leccion', 'Modulo_id'),
    'Material_leccion': ('Id_material', 'Leccion_id'),
    'Inscripcion': ('Id_Inscripcion', 'Usuario_id', 'Curso_id', 'Estado', 'Fecha_inscripcion'),
    'Suscripcion': ('Id_suscripcion', 'Usuario_id', 'Plan_id', 'Estado'),
    'Pago': ('Id_pago', 'Suscripcion_id', 'Estado', 'Monto', 'Moneda'),
    'Detalle_estudiante': ('Id_detalle_estudiante', 'Usuario_id'),
    'Detalle_Profesor': ('Id_detalle_profesor', 'Usuario_id'),
    'Certificado': ('Id_certificado', 'Usuario_id', 'Curso_id', 'Fecha_emision'),
}

RELACIONES = {
    'Curso': {'Profesor_id': 'Usuario'},
    'Modulo': {'Curso_id': 'Curso'},
    'Leccion': {'Modulo_id': 'Modulo'},
    'Material_leccion': {'Leccion_id': 'Leccion'},
    'Inscripcion': {'Usuario_id': 'Usuario', 'Curso_id': 'Curso'},
    'Suscripcion': {'Usuario_id': 'Usuario', 'Plan_id': 'plan'},
    'Pago': {'Suscripcion_id': 'Suscripcion'},
    'Detalle_estudiante': {'Usuario_id': 'Usuario'},
    'Detalle_Profesor': {'Usuario_id': 'Usuario'},
    'Certificado': {'Usuario_id': 'Usuario', 'Curso_id': 'Curso'},
}


def cargar_tablas(archivo):
    with pd.ExcelFile(archivo, engine='openpyxl') as libro:
        return {nombre: libro.parse(nombre, header=1, usecols=list(columnas))
                for nombre, columnas in TABLAS.items()}


def diagnosticar_claves(tablas):
    resumen = []
    for nombre, tabla in tablas.items():
        llave = tabla[TABLAS[nombre][0]]
        huerfanas = 0
        for campo, padre in RELACIONES.get(nombre, {}).items():
            esperadas = tablas[padre][TABLAS[padre][0]].dropna()
            presentes = tabla[campo].dropna()
            huerfanas += int((~presentes.isin(esperadas)).sum())
        resumen.append({'tabla': nombre, 'filas': len(tabla),
                        'claves_nulas': int(llave.isna().sum()),
                        'claves_repetidas': int(llave.dropna().duplicated().sum()),
                        'referencias_huerfanas': huerfanas})
    return resumen


def estado(serie):
    return serie.astype('string').str.strip().str.lower()


def centavos(valor):
    return int((Decimal(str(valor)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def resumir_planes(tablas):
    suscripciones = tablas['Suscripcion']
    pagos = tablas['Pago'].copy()
    if set(pagos['Moneda'].dropna()) != {'USD'} or pagos['Moneda'].isna().any():
        raise ValueError('El resumen monetario requiere que todos los pagos estén en USD.')
    pagos['completado'] = estado(pagos['Estado']).eq('completado').fillna(False)
    pagos['centavos_cobrados'] = pagos['Monto'].where(pagos['completado'], 0).map(centavos)
    pagos_con_plan = pagos.merge(suscripciones[['Id_suscripcion', 'Plan_id']], how='left',
                                left_on='Suscripcion_id', right_on='Id_suscripcion', validate='many_to_one')
    if pagos_con_plan['Plan_id'].isna().any() or suscripciones['Plan_id'].isna().any():
        raise ValueError('Hay pagos o suscripciones sin un plan trazable.')

    por_suscripcion = suscripciones.groupby('Plan_id').size().rename('suscripciones')
    por_pago = pagos_con_plan.groupby('Plan_id').agg(
        intentos=('Id_pago', 'size'), completados=('completado', 'sum'),
        centavos_cobrados=('centavos_cobrados', 'sum'),
    )
    planes = (tablas['plan'].set_index('Id_plan')[['Nombre']]
              .join(por_suscripcion).join(por_pago).fillna(0))
    campos = ['suscripciones', 'intentos', 'completados', 'centavos_cobrados']
    planes[campos] = planes[campos].astype(int)
    planes = planes.rename(columns={'Nombre': 'plan'}).sort_values('centavos_cobrados', ascending=False)
    filas = planes.to_dict('records')
    assert sum(fila['suscripciones'] for fila in filas) == len(suscripciones)
    assert sum(fila['intentos'] for fila in filas) == len(pagos)
    return filas


def resumir_aprendizaje(tablas):
    cursos = tablas['Curso'][['Id_curso', 'Categoria']]
    inscripciones = tablas['Inscripcion'].copy()
    certificados = tablas['Certificado'].copy()
    clave = ['Usuario_id', 'Curso_id']
    if inscripciones.duplicated(clave).any() or certificados.duplicated(clave).any():
        raise ValueError('Se requiere una inscripción y un certificado como máximo por persona y curso.')

    inscripciones['completado'] = estado(inscripciones['Estado']).eq('completado').fillna(False)
    inscripciones['abandonado'] = estado(inscripciones['Estado']).eq('abandonado').fillna(False)
    inscripciones['Fecha_inscripcion'] = pd.to_datetime(inscripciones['Fecha_inscripcion'], errors='coerce')
    certificados['Fecha_emision'] = pd.to_datetime(certificados['Fecha_emision'], errors='coerce')
    recorrido = (inscripciones.merge(certificados[clave + ['Id_certificado', 'Fecha_emision']],
                                    on=clave, how='outer', validate='one_to_one', indicator=True)
                 .merge(cursos, left_on='Curso_id', right_on='Id_curso', how='left', validate='many_to_one'))
    intervalo = recorrido['Fecha_emision'] - recorrido['Fecha_inscripcion']
    dias = intervalo.dt.total_seconds() / 86400
    recorrido['dias'] = dias.map(lambda valor: int(valor) if pd.notna(valor) else pd.NA).astype('Int64')
    recorrido['duracion_negativa'] = intervalo.lt(pd.Timedelta(0))
    recorrido['dias_validos'] = recorrido['dias'].where(~recorrido['duracion_negativa'])
    recorrido['inscrito'] = recorrido['_merge'].ne('right_only')
    recorrido['certificado'] = recorrido['Id_certificado'].notna()
    por_categoria = recorrido.groupby('Categoria', dropna=False).agg(
        inscripciones=('inscrito', 'sum'), finalizadas=('completado', 'sum'),
        abandonadas=('abandonado', 'sum'), certificados=('certificado', 'sum'),
        fechas_invertidas=('duracion_negativa', 'sum'), pares_con_dias_validos=('dias_validos', 'count'),
        media_dias_validos=('dias_validos', 'mean'),
    ).reset_index().rename(columns={'Categoria': 'categoria'})
    por_categoria['media_dias_validos'] = por_categoria['media_dias_validos'].round(2)
    por_categoria = por_categoria.sort_values('inscripciones', ascending=False)
    filas = json.loads(por_categoria.to_json(orient='records', force_ascii=False))
    assert sum(fila['inscripciones'] for fila in filas) == len(inscripciones)
    assert sum(fila['certificados'] for fila in filas) == len(certificados)
    personas_inscritas = tablas['Usuario'].loc[tablas['Usuario']['Id_usuario'].isin(inscripciones['Usuario_id'])]
    assert recorrido['dias_validos'].notna().any(), 'Se necesita al menos un par válido para calcular la duración'
    audit = {'inscripciones': len(inscripciones), 'finalizadas': int(inscripciones['completado'].sum()),
             'abandonadas': int(inscripciones['abandonado'].sum()), 'certificados': len(certificados),
             'personas_con_inscripcion': int(inscripciones['Usuario_id'].nunique()),
             'personas_inscritas_por_rol': {str(k): int(v) for k, v in estado(personas_inscritas['Rol']).value_counts().items()},
             'certificados_sin_inscripcion': int(recorrido['_merge'].eq('right_only').sum()),
             'certificados_sin_fechas_validas': int((recorrido['certificado'] & recorrido['dias'].isna()).sum()),
             'fechas_invertidas': int(recorrido['duracion_negativa'].sum()),
             'media_dias_original': round(float(recorrido['dias'].mean()), 2),
             'media_dias_validos': round(float(recorrido['dias_validos'].mean()), 2)}
    return filas, audit


def generar_extracto(tablas):
    calidad = diagnosticar_claves(tablas)
    if any(t['claves_nulas'] or t['claves_repetidas'] for t in calidad):
        raise ValueError('Hay claves primarias inválidas. Revisa diagnosticar_claves antes de calcular indicadores.')
    categorias, aprendizaje = resumir_aprendizaje(tablas)
    aprendizaje['cursos_publicados'] = int(tablas['Curso']['Publicado'].eq(1).sum())
    return {'fuente': 'PowerBI_Aprendia_Paquete.xlsx', 'tablas': calidad,
            'categorias': categorias, 'aprendizaje': aprendizaje, 'planes': resumir_planes(tablas)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archivo', type=Path, help='Extracto original en Excel')
    parser.add_argument('--salida', type=Path, default=Path('datos/corte_agregado.json'))
    args = parser.parse_args()
    resultado = generar_extracto(cargar_tablas(args.archivo))
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_bytes((json.dumps(resultado, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


if __name__ == '__main__':
    main()
