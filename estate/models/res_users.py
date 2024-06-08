from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    _name = 'res.users'
    _description = 'herencia de res.users'

    property_ids = fields.One2many('estate.propiedad', 'seller_id')
