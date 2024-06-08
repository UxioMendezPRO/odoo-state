from odoo import fields, models, api


class Type(models.Model):
    _name = 'estate.property.type'
    _description = 'Tipos de propiedades '
    # Orden
    _order = 'name'

    name = fields.Char('Nombre', required=True)
    property_ids = fields.One2many('estate.propiedad', 'property_type_id')
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute="_compute_offer_count", string="Ofertas", default=0)

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            print(record.name)
            print("Número de ofertas",
                  len(list(record.offer_ids)))
            record.offer_count = len(list(record.offer_ids))
            print(record.offer_count)
