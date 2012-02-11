from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from models import Confirmation

class ConfirmationAdmin(admin.ModelAdmin):
    list_display = ('shopper_id', 'ret_transdatetime', 'addr_name', 'trx_amount',
                    'trx_currency', 'ret_status')
    fieldsets = (
        (None, {
            'fields': ('shopper_id', 'ret_status', 'vendor_comment')
        }),
        (_('Payment details'), {
            'fields': ('ret_transdatetime', 'trx_paymentmethod', 'addr_name',
                       'trx_amount', 'trx_currency', 'trx_paymenttyp')
        }),
        (_('Customer identification'), {
            'fields': ('ret_ip', 'trx_remoteip_country')
        }),
        (_('Transaction information'), {
            'fields': ('ret_booknr', 'ret_errorcode', 'ret_trx_number', 
                       'ret_authcode', 'trx_typ', 'trxuser_id')
        }),
    )
    readonly_fields = ('shopper_id', 'ret_booknr', 'ret_errorcode',
        'trx_paymentmethod', 'ret_trx_number', 'ret_transdatetime', 'ret_ip',
        'trx_typ', 'addr_name', 'trx_amount', 'trx_remoteip_country',
        'trx_currency', 'ret_authcode', 'trx_paymenttyp', 'ret_status',
        'trxuser_id'
    )


admin.site.register(Confirmation, ConfirmationAdmin)
