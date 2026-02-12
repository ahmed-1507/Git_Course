from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.osv import expression


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'

    name = fields.Char(string='Patient',required=True)
    birthdate = fields.Date()
    country = fields.Char()
    email = fields.Char()
    age = fields.Integer(string='Age',compute='_compute_age')
    full_age = fields.Char(string="Full Age", compute="_compute_full_age")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')])
    address = fields.Text()
    ref = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                      default=lambda self: ('New'))
    lab_results_url = fields.Char(string="Lab Results Link")



    _sql_constraints = [('unique_name', 'UNIQUE(name)', 'name exists'),
                        # ('check_age', 'CHECK(age<18)', 'age must be bigger than 18'),
                        ]

    @api.depends('birthdate')
    def _compute_age(self):
        for rec in self:
            today = fields.Date.today()
            if rec.birthdate and today >= rec.birthdate:
                rec.age = today.year - rec.birthdate.year
            else:
                rec.age = 0

            if rec.birthdate:
                delta = relativedelta(today, rec.birthdate)
                rec.full_age = f"{delta.years} years, {delta.months} months, {delta.days} days"
            else:
                rec.full_age = "N/A"


    @api.constrains('birthdate')
    def Check_age(self):
        for rec in self:
            today = fields.Date.today()
            if rec.birthdate and rec.birthdate > today:   # if rec.fieldName and rec.fieldName bla bla  --> syntax to avoid boolean errors
                raise ValidationError("Please Enter A Valid Birthdate")



    def view_lab_results(self):
        self.ensure_one()
        if not self.lab_results_url:
            raise ValidationError("No lab results link found for this patient.")
        return {
            'type': 'ir.actions.act_url',
            'url': self.lab_results_url,
            'target': 'new',
        }

    @api.model
    def name_create(self, name):
        print('self',
              self)  # "وده معناه انك لو طبعت ال self قبل ال res هترجع object فاضي لاني بالفعل لسه الفانكشن مشتغلتش ومعملش كرييت للريكورد "
        print('name', name)  # "ده الاسم اللي اليوزر هيدخله من الانترفيس"
        res = super(HospitalPatient, self).name_create(name)
        print('res', res)  # "لكن بمجرد ما تيجي للسطر بتاع ال res فا كده الفانكشن اشتغلت وبقي معاك ريكورد ف ايدك "
        return res

        # or
    # @api.model
    # def name_create(self, name):
    #     print("lllllllllllllllllllllllllllllllllllllllll")
    #     return self.create({'name': name , 'email':'test@email.com'}).name_get()[0]
    ##     #********************************************************************************************


    def view_patient_prescription(self):
        # عشان تنادي علي ريكورد معين في ملف xml من داخل ملف البايثون
        # action = self.env.ref('hospital_management.hospital_doctor_view_action').read()[0]
        # return action

        #or
        # return self.env['ir.actions.act_window']._for_xml_id('hospital_management.hospital_doctor_view_action')

        #or
        # action = self.env["ir.actions.actions"]._for_xml_id('hospital_management.hospital_prescription_view_action')
        # action['views'] = [(self.env.ref('hospital_management.hospital_prescription_view_tree').id, 'tree')]
        # action['res_id'] = self.id
        # action['domain'] = [('patient_id', '=', self.id)]
        # return action

        #or
        domain = [('patient_id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.prescription',
            'view_mode': 'tree',
            'domain': domain,
            'target': 'new',
        }

    # --------------------------------------------------------------------------
    # def cancel_day(self):
    #     date_cancel = fields.Integer('Date Cancel')
    #     cancel_day = self.env['ir.config_parameter'].sudo().get_param('law_office.cancel_days')
    #     allowed_day = self.interview_time.day - relativedelta.relativedelta(days=int(cancel_day))
    #     if allowed_day > date.today():
    #         raise ValueError(";;;;;;;;;;;;;;;;;;;;;;;;;;;")

    # -------------------------------------------------------------------------------

    # customers = fields.Integer(string='customer count', compute='print_read')
    # customer_ids = fields.One2many(comodel_name='customer.office', inverse_name='employee_id')
    #
    # @api.depends('customer_ids')  # depends on field many2many or many2one with searched model
    # def print_read(self):
    #     for record in self:
    #         domain = [('employee_id', '=', record.id)]
    #         searched_names = self.env['customer.office'].search(domain)     #return list of recordsets
    #         searched_names = self.env['customer.office']._search(domain)      # return list of ids
    #         searched_count = self.env['customer.office'].search_count(domain)
    #         search_group = self.env['customer.office'].read_group(
    #             domain=domain,
    #             fields=['employee_id'],
    #             groupby=['employee_id'],
    #         )
    #         # print('search------------', searched_names)
    #         # print('count--------', searched_count)
    #         # print('group-----------', search_group)
    #
    #         for rec in search_group:
    #             count = rec['employee_id_count']
    #             name_id = rec['employee_id'][0]
    #
    #             employee_rec = self.env['employee.office'].browse(name_id)
    #             employee_rec.customers = count
    #             self = self - employee_rec  # to avoid error occuring because off calculation of nothing computed field
    #             self.customers = 0
    #
    #             print(name_id)
    #             print(count)
    #             print(employee_rec)
    # -------------------------------------------------------------------------------

    # employee = self.env['employee.office']
    # ids = [1,2,3,4,5]        #اي ارقام عشوائيه
    # employee_ids = employee.browse(ids)
    # 1>>>>>>>>  for emp in employee_ids:
    #     try:
    #         emp.id
    #
    #     except Exception as e :
    #         print("this record %d isn't exist " %(emp) )
    #
    # 2>>>>>>>>> for emp in employee_ids:
    #     if emp.exists():
    #         emp.id
    #     else:
    #         print("this record %d isn't exist " % (emp))

    # -------------------------------------------------------------------------------

# # (لو عايز اعمل انهيرت لفانكشن هي اساسا معمولها انهيرت جوه اودوو )
# # (وهعرف ازاي انها معمولها انهيرت == هتلاقيه عامل ريترن للسوبر  )
# # (ساعتها لو عايز اعملها انهيرت هعملها import from model path by class name  )
# # (from odoo.addons.sale.models.sale import SaleOrder as OdooSaleOrder)
# # (وساعتها اخد الفانكشنن كلها عندي واغير فيها براحتي )