import sys
sys.path.append('.')
from modules.marketplace import marketplace
from src import db

# Verificar que la parcela se guardó con coordenadas
plots = db.get_all_plots()
if not plots.empty:
    print('📊 Parcelas en la base de datos:')
    for idx, plot in plots.iterrows():
        if plot['catastral_ref'] == '1234567ABC1234':
            print('✅ Parcela de prueba encontrada:')
            print('   Título:', plot['title'])
            print('   Municipio:', plot['locality'])
            print('   Coordenadas:', f'{plot["lat"]:.4f}, {plot["lon"]:.4f}')
            print('   Estado:', plot['status'])
            break
    else:
        print('❌ Parcela de prueba no encontrada')
else:
    print('❌ No hay parcelas en la base de datos')