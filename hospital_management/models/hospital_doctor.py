
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
from dateutil import relativedelta

class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Doctor'

    name = fields.Char(string='Doctor', required=True,tracking=1)
    specialization = fields.Selection([
        ('pediatrics', 'Pediatrics'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('dermatology', 'Dermatology'),
        ('gynecology', 'Gynecology'),
        ('ent', 'ENT (Ear, Nose, Throat)'),
        ('radiology', 'Radiology'),
        ('surgery', 'General Surgery'),
        ('dentistry', 'Dentistry'),
    ], string="Specialization", required=True,tracking=2)
    birthdate = fields.Date()
    age = fields.Integer(string='Age',inverse='_inverse_computed_age',)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')])
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone',tracking=3)
    country = fields.Char()
    available_days_ids = fields.Many2many('hospital.weekday', string='Available Days')
    appointment_ids = fields.One2many('hospital.appointment','doctor_id', string='Appointment')
    user_id = fields.Many2one('res.users', tracking=True,string='User',
                                      default=lambda self: self.env.user)
    priority = fields.Selection([('0', 'Very bad'),  # لاظهار النجوووووم للتقييم
                                 ('1', 'good'),
                                 ('2', 'very good'),
                                 ('3', 'excellent')],
                                string='Priority')
    # vedio 94 weblearn
    #     roll_name = fields.Char(tracking=True)
    #
    #     def _change_manager_roll_name(self , add_string):
    #
    #         manager = self.search([('roll_name' , '=' , False)])
    #         for man in manager:
    #             man.roll_name = add_string +'Man' + str(man.id)

    website = fields.Char(tracking=True)
    description = fields.Text()
    prescription = fields.Html()
    documents = fields.Binary()
    document_name = fields.Char()
    image = fields.Image(max_width=150, max_height=150)
    marital_status = fields.Selection([
        ('married', 'Married'),
        ('single', 'Single'),
        ('divorced', 'Divorced'),
    ])


    # (اللوجيك اني اخلي فيلد ال age يبقي readonly لانه هيتحسب تلقائي من ال onchange )
    # (فلما هعمله readonly من ملف البايثون واروح انشئ ريكورد هلاقي قيمة الفيلد هتختفي لما ادوس حفظ .. والحل اني احط للفيلد force_save="1" في ملف ال xml  )
    @api.onchange('birthdate')
    def _onchange_calc_age(self):
        for rec in self:
            today = fields.Date.today()
            if rec.birthdate:
                if today >= rec.birthdate:
                    rec.age = today.year - rec.birthdate.year
                    return {'warning': {
                        'title': 'age calculating',
                        'message': 'age changed successfully'
                    }}
                else:
                    raise ValidationError("Please Enter A Valid BirthDate")



    # team_ids = fields.One2many(comodel_name='employee.office', inverse_name='team_id', string='Team')

    # employee_idd = fields.Many2one('employee.office' , ondelete='restrict' , domain=[('age','<',30),('years_experience','>',3)])
    # # Dynamic filter for Many2one Field | Return domain using onchange method
    # # vedio number 100 in weblearnes
    # @api.onchange("employee_idd")
    # def _onchange_user_id(self):
    #     emp_id = 0
    #     if self.employee_idd:
    #         emp_id = self.employee_idd.id
    #     return {"domain": {"id": [("id", "=", emp_id)]}}
    #     return {"domain": {"field_name": [("field_name", "=", value)]}}



    @api.depends('age')
    def _inverse_computed_age(self):
        for rec in self:
            rec.birthdate = datetime.date.today()- relativedelta.relativedelta(years=rec.age)


    @api.ondelete(at_uninstall=False)
    def check_delete(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(f"you can not delete because doctor {rec.name} have an appointment")

#     #--------------------------------------------------------------------------------------



# #وممكن ننادي ع الويزارد من خلال زرار نوعه اكشن في ملف ال xml
#     # < button name = "law_office.wizard_action" type = "action" string = "open wizard" class ="oe_highlight" / >
#
# # وممكن ننادي علي الويزارد من خلال الاكشن مينو عن طريق اني اعملها ريكورد شبيه بالريكزرد اكشن هتلاقيه معمول ف فايل ال wizard_employee_view من تحت

# # وممكن ننادي علي الويزارد من خلال menuitem عن طريق اني اعملها ريكورد هتلاقيه معمول ف فايل ال wizard_employee_view من تحت

#     #-------------------------------------------------------------------------
    @api.model
    def create(self, vals):
        if not vals['country']:
            # if vals['country'] == False    or =====> if vals.get('country') == False    or ====> if nor vals.get('country')
            vals['country'] = 'egypt'
        res = super(HospitalDoctor, self).create(vals)

        # " كل ما هو قبل ال res كاني لسه بدخل داتا للريكورد من الانترفيس عادي لسه معملتش كرييت للريكورد "
        # "وده معناه انك لو طبعت ال self قبل ال res هترجع object فاضي لاني بالفعل لسه الفانكشن مشتغلتش ومعملش كرييت للريكورد "
        # "فلما تيجي تعمل اساين لقيمة فيلد هتبقي مجرد ابديت علي الdectionary بتاع ال values عادي زي كده vals['name']=value  "
        # "لكن بمجرد ما تيجي للسطر بتاع ال res فا كده الفانكشن اشتغلت وبقي معاك ريكورد ف ايدك فلما تيجي تعمل اساين لقيمة فيلد هتبقي res.field=value"

        app_no = 0
        for app in res.appointment_ids:
            app_no += 1
            app.app_no = app_no

        # browsed_employee = self.env['employee.office'].browse(vals.get('employee_idd'))
        # for rec in browsed_employee:
        #     rec.description = 'text from ,my current creation func'  # كده لما هختار موظف وانا بنشئ مدير هيطبعلي تلقائي عند الموظف اللي اختارته ده ان الوصف بالجمله دي

        return res
        # عشان تتعامل مع علاثه one2many وت access عليها هتحط ال super في متغير وتنادي علي الفيلد ده بال dot notation
        # يبقي اي فيلد قبل ال res يبقيvals['fieldname'] واي فيلد بعد ال res يبقي res.fieldname

#     #********************************************************************************************

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        print('allfields',allfields)
        print('attributes',attributes)

        """ fields_get([allfields][, attributes])
        Return the definition of each field.

        The returned value is a dictionary (indexed by field name) of
        dictionaries. The _inherits'd fields are included. The string, help,
        and selection (if present) attributes are translated.

        :param list allfields: fields to document, all if empty or not provided
        :param list attributes: attributes to return for each field, all if empty or not provided
        :return: dictionary mapping field names to a dictionary mapping attributes to values.
        :rtype: dict
        """
        res = {}
        for fname, field in self._fields.items():
            if allfields and fname not in allfields:
                continue
            if field.groups and not self.env.su and not self.user_has_groups(field.groups):
                continue

            description = field.get_description(self.env, attributes=attributes)
            res[fname] = description
        return res



    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None, name_get_uid=None):
        domain = domain or []
        if name:
            name_domain = ['|', ('name', operator, name), ('age', operator, name)]
            domain += name_domain
        return self._search(domain, limit=limit, order=order, access_rights_uid=name_get_uid)

    # @api.model
    # def _name_search(self, name,domain=None, operator='ilike', limit=100, order=None):
    #     domain = domain or []
    #     if name:  # يnameقصده بيها ال rec_name اللي بيظهر تلقائي كاسم للريكورد وليس ال name الفيلد بتاعيى
    #         domain += expression.AND([['|','|', ('name', operator, name),('age', operator, name), ('country', operator, name)], domain])
    #     # فانا بقوله ان كل الفيلدات اللي جوه الdomain عاملهم كانهم rec_name وحطهم كعناصر بحث تلقائي
    #     return self._search(domain , limit=limit, order=order)

    # self._search()   ===>  will return list of ids of the matching records
    # self.search()   ===>  will return record sets of the matching records

#     # --------------------------------------------------------------------------------
#     # (لو عايز اخفي جروب من شاشة اليوزر)
#     class GroupsView(models.Model):
#         _inherit = 'res.groups'
#
#         @api.model
#         def get_application_groups(self, domain):
#             # Overridden in order to remove 'Show Full Accounting Features' and
#             # 'Show Full Accounting Features - Readonly' in the 'res.users' form view to prevent confusion
#             group_account_user = self.env.ref('account.group_account_user', raise_if_not_found=False)
#             # account.group_account_user ==> (هجيبه من شاشة اسم الجروب نفسه وادوس علس view meta data)
#             if group_account_user and group_account_user.category_id.xml_id == 'base.module_category_hidden':
#                 domain += [('id', '!=', group_account_user.id)]
#             group_account_readonly = self.env.ref('account.group_account_readonly', raise_if_not_found=False)
#             if group_account_readonly and group_account_readonly.category_id.xml_id == 'base.module_category_hidden':
#                 domain += [('id', '!=', group_account_readonly.id)]
#             return super().get_application_groups(domain)

