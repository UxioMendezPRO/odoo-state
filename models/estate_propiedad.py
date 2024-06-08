from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class Property(models.Model):
    _name = 'estate.propiedad'
    _description = 'Propiedades Inmobiliaria'

    # Constraints de SQL. Tienen que ir al principio

    _sql_constraints = [
        ("check_precio_esperado", "CHECK(precio_esperado >= 0)", "El precio esperado debe ser positivo"),
        ("check_precio_venta", "CHECK(precio_venta >= 0)", "El precio de venta debe ser positivo"),
    ]

    # Atributos

    nombre = fields.Char('Nombre', required=True)
    descripcion = fields.Text('Descripción')
    cp = fields.Char('Código postal')
    fecha_disponibilidad = fields.Date('Fecha de disponibilidad', copy=False)
    precio_esperado = fields.Float('Precio esperado', required=True)
    precio_venta = fields.Float('Precio de venta', readonly=True, copy=False)
    dormitorios = fields.Integer('Dormitorios', default=2)
    area_habitable = fields.Integer('Área habitable')
    fachadas = fields.Integer('Fachadas')
    garaje = fields.Boolean('Garaje')
    jardin = fields.Boolean('Jardín')
    area_jardin = fields.Integer('Área de jardín')
    activo = fields.Boolean(default=True)

    # Orden
    _order = "id desc"

    # Selecciones

    orientacion_jardin = fields.Selection(string='Orientación',
                                          selection=[('norte', 'Norte'), ('sur', 'Sur'), ('este', 'Este'),
                                                     ('oeste', 'Oeste')])

    state = fields.Selection(string='estado',
                             selection=[('nueva', 'Nueva'),
                                        ('oferta_recibida', 'Oferta recibida'),
                                        ('vendida', 'Vendida'),
                                        ('oferta_aceptada', 'Oferta Aceptada'),
                                        ('cancelada', 'Cancelada'), ],
                             required=True,
                             copy=False,
                             default="nueva")

    # Tipos Many2one

    property_type_id = fields.Many2one('estate.property.type', string='Tipo')
    seller_id = fields.Many2one("res.users", string="Vendedor", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Comprador", readonly=True)

    # Tags many2many

    tags_id = fields.Many2many('estate.property.tag', string='Etiqueta')

    # Ofertas

    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Oferta')

    # Atributos calculados

    total_area = fields.Float(compute="_compute_total", string="Área total")

    @api.depends('area_habitable', 'area_jardin')
    def _compute_total(self):
        for record in self:
            record.total_area = record.area_habitable + record.area_jardin

    # Calculos con atributos relacionados

    best_offer = fields.Float(compute="_compute_best_offer", string="Mejor oferta", default="0.0")

    @api.depends('offer_ids')
    def _compute_best_offer(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            if not prices:
                record.best_offer = 0.0
            else:
                record.best_offer = max(prices)

    @api.onchange('jardin')
    def _onchange_jardin(self):
        if self.jardin:
            self.area_jardin = 10
            self.orientacion_jardin = 'norte'
        else:
            self.orientacion_jardin = None
            self.area_jardin = None

    # Acciones

    def action_cancel(self):
        if self.state == 'vendida':
            raise UserError("Propiedad vendida. No puede cancelarse")
        else:
            self.state = 'cancelada'

    def action_sell(self):
        if self.state == 'cancelada':
            raise UserError("Propiedad cancelada. No puede venderse")
        else:
            self.state = 'vendida'

    # Constraints de oferta
    @api.constrains('precio_venta', 'precio_esperado')
    def check_price(self):
        for record in self:
            if record.precio_venta < record.precio_esperado * 0.90 and record.precio_venta != 0.0:
                raise ValidationError("El precio de venta es demasiado bajo")

    # Comprobador de ofertas
    @api.onchange('offer_ids')
    def check_offers(self):
        for record in self:
            if len(record.offer_ids) > 0:
                record.state = 'oferta_recibida'

    # On delete
    @api.ondelete(at_uninstall=False)
    def _unlink_if_cancelled(self):
        for order in self:
            if self.state not in ('cancelada', 'nueva'):
                raise UserError("No puede borrarse una propiedad que no está cancelada")


