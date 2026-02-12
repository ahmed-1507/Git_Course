from email.policy import default
from odoo import models , fields , api
from datetime import timedelta

class HospitalMedicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Medicine'

    name = fields.Char(string="Name",required=True)
    description = fields.Text(string="Description")
    stock_qty = fields.Integer(string="Stock Quantity")

    price = fields.Float(string="Price/Unit" ,digits='Product Price')   #digits--> sittings/tichnical/Decimal accuracy
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', related='user_id.company_id')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)

    color_1 = fields.Integer(string="Color 1")  # for widget='color_picker'
    color_2 = fields.Char(string="Color 2")  # for widget='color'

    # فيلد  selsction --reference  عادي بس الاختيارات بتبقي models مش fields وبيربطلي بينهم بعلاقه many2one
    # and selection field will store his data in the dataase as a string not integer
    reference = fields.Reference(selection=[('res.company' , 'Company') , ('res.currency' , 'Currency')])

    production_date = fields.Date(string="Production Date",default=fields.Date.today)
    available_duration = fields.Float(string="Available Duration")
    expiration_date = fields.Date(string="Expiration Date", store=True,
                           compute='_get_expiration_date', inverse='_set_expiration_date')


    # employee_id = fields.Many2one('employee.office' , ondelete='cascade')
#     # ----------------------------------------------------------------------------
    so_method = fields.Integer(string='so counts' , compute='show_counts')
    user_ids = fields.Many2many('sale.order')
    #   #مش محتاج اظهر في الفيو فورم الفيلد ال many2many ده انا بس بعمله علاقه مع الموديل اللي عايز اخد منه الداتا عشان اعمل depend عليه في decorator
    @api.depends('user_ids')
    def show_counts(self):
        domain = [('partner_id', '=', self.user_id.id)]
        filtered_customer = self.env['sale.order'].search_count(domain)
        self.so_method = filtered_customer

#     #ال partner_id عباره عن many2one مع ال res.partner ودي محطوطه ف موديل ال sale.order مش موديل ال res.partner يبقي هترجع id فلما اساويها بال user_id بتاعي لازم ا access ال id منه



    #_compute_display_name معادية ال name_get اتغيرت في فيرجن 17 بقت
    # def name_get(self):
    #    return [(rec.id, "[%s],(%s)" % (rec.name, rec.stock_qty))for rec in self]
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.name}],({record.stock_qty})"

    @api.depends('production_date', 'available_duration')
    def _get_expiration_date(self):
        for r in self:
            if not (r.production_date and r.available_duration):
                r.expiration_date = r.production_date
                continue

            # Add available_duration to production_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.production_date)
            available_duration = timedelta(days=r.available_duration, seconds=-1)
            r.expiration_date = start + available_duration

    def _set_expiration_date(self):
        for r in self:
            if not (r.production_date and r.expiration_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            production_date = fields.Datetime.from_string(r.production_date)
            expiration_date = fields.Datetime.from_string(r.expiration_date)
            r.available_duration = (expiration_date - production_date).days + 1


