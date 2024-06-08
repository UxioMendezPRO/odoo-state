from odoo import fields, models, api


class EstateProperty(models.Model):
    _inherit = 'estate.propiedad'

    _name = 'estate.propiedad'
    _description = 'Herencia de estate property'

    def action_sell(self):
        print("llamada a la función sobrescrita")
        invoice = self.env['account.move'].create(
            {'partner_id': self.id,
             'move_type': 'out_invoice',
             'name': self.nombre,
             'line_ids': [(
                 0,
                 0,
                 {
                     "quantity": 1,
                     "price_unit": self.precio_venta * 1.06 + 100.00,
                 }
             )], })
        print("Creado invoice")
        return super().action_sell()
