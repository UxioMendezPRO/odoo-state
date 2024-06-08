from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Ofertas'
    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0)', 'El precio debe ser positivo'),
    ]
    _order = 'price desc'

    # Atributos

    price = fields.Float('Precio')
    status = fields.Selection(string='Estado',
                              selection=[('accepted', 'Aceptada'),
                                         ('refused', 'Rechazada')], readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required='True')
    property_id = fields.Many2one('estate.propiedad', string='ID Propiedad', required=True)
    validity = fields.Integer(string='Validez (días)', default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_validity", string="Fecha límite",
                                default=fields.Date.today() + timedelta(days=7))

    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    # Métodos de fechas
    @api.depends('date_deadline')
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + timedelta(days=record.validity)

    def _inverse_validity(self):
        for record in self:
            days = record.date_deadline - record.create_date.date()
            record.validity = days.days

    # Métodos de ofertas
    @api.depends('property_id')
    def action_accept_offer(self):
        for record in self:
            if record.property_id.state == 'oferta_aceptada':
                raise UserError("Ya existe una oferta aceptada")
            else:
                self.status = 'accepted'
                record.property_id.precio_venta = self.price
                record.property_id.buyer_id = self.partner_id
                record.property_id.state = 'oferta_aceptada'
                for offer in record.property_id.offer_ids:
                    if offer != self:
                        offer.status = 'refused'

    def action_refuse_offer(self):
        if self.status != 'refused':
            self.status = 'refused'
        for record in self:
            for offer in record.property_id.offer_ids:
                record.property_id.precio_venta = 0
                record.property_id.buyer_id = None
                record.property_id.state = 'nueva'

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id', False)  # Evita fallo si no hay propiedad
        this_property = self.env['estate.propiedad'].browse(property_id)
        if this_property:
            if this_property.best_offer:
                if vals['price'] < this_property.best_offer:
                    raise UserError("Oferta demasiado baja")
        return super(Offer, self).create(vals)
