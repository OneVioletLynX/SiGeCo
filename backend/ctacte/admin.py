# from django.contrib import admin
# from .models import MesPago, MetodoPago, Pago, PagoDetalle

# @admin.register(MesPago)
# class MesPagoAdmin(admin.ModelAdmin):
#     list_display = ('id_mes', 'descripcion')
#     search_fields = ('descripcion',)

# @admin.register(MetodoPago)
# class MetodoPagoAdmin(admin.ModelAdmin):
#     list_display = ('id_metodo_pago', 'descripcion')
#     search_fields = ('descripcion',)

# @admin.register(Pago)
# class PagoAdmin(admin.ModelAdmin):
#     list_display = ('id_pago', 'fecha_pago', 'alumno', 'importe_total', 'metodo_pago', 'usuario')
#     list_filter  = ('metodo_pago', 'fecha_pago')
#     search_fields = ('alumno__apellido', 'alumno__nombre')
#     autocomplete_fields = ('alumno', 'usuario')

# @admin.register(PagoDetalle)
# class PagoDetalleAdmin(admin.ModelAdmin):
#     list_display = ('id_detalle', 'pago', 'mes', 'importe')
#     list_filter  = ('mes',)
#     search_fields = ('pago__alumno__apellido', 'pago__alumno__nombre')
