from odoo import fields, models


class Tag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Tags propiedades'
    # Constraints
    _sql_constraints = [
        ('price_unique', 'unique (name)', 'La etiqueta debe ser única'),
    ]
    # Orden
    _order = 'name'

    # Atributos
    name = fields.Char('Nombre', required=True)
    color = fields.Integer('Color')
