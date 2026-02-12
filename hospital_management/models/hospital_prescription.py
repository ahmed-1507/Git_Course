from email.policy import default

from odoo import models,fields,api,_
from datetime import datetime
from odoo.exceptions import ValidationError


class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Prescription'



    def get_default_date_field(self):
        return fields.Datetime.now()

    name = fields.Char('Sequence', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', readonly=True)
    doctor_id = fields.Many2one('hospital.doctor' , readonly=True)
    appointment_id = fields.Many2one('hospital.appointment',string="Appointment")
    date = fields.Datetime(default=lambda pr: pr.get_default_date_field())
    prescription_line_ids = fields.One2many('hospital.prescription.line', 'prescription_id')

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', related='user_id.company_id')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", store=True)

    medicine_color_ids = fields.Many2many(comodel_name='hospital.medicine' , string='Medicines')
    # #بستخدم ال view ال color بتاع الموديل اللي ف العلافه عشان لما اختار موظف يظهر بنفس لونه  ف الموديل بتاعه


    @api.depends('prescription_line_ids.price_subtotal')
    def _compute_total_amount(self):
        for rec in self:
            # rec.total_amount = sum(rec.prescription_line_ids.mapped('price_subtotal'))

            # or
            rec.total_amount = sum(line.price_subtotal for line in rec.prescription_line_ids)

    @api.model_create_multi
    def create(self, vals):
        for value in vals:
            if not value.get('name') or value.get('name') == 'New':
                value['name'] = self.env['ir.sequence'].next_by_code('hospital.prescription')

        res = super(HospitalPrescription, self).create(vals)
        lines_count = 0
        for line in res.prescription_line_ids:
            lines_count += 1
            line.lines_count = lines_count
        return res


    def write(self, vals):
        res = super(HospitalPrescription, self).write(vals)
        lines_count = 0
        for line in self.prescription_line_ids:
            lines_count += 1
            line.lines_count = lines_count

        # print(res)     will print boolean value if your new data updated in data base or not
        # "عشان كده بخلي ال res في متغير واكتب بعدها اللوجيك بتاعي وبعدها اعمل ريترن ال res لان في الحاله دي ال res مش الريكورد لالا دي هترجع بوليان فاليو اذا كانت الداتا الجديده سمعت في الداتا بيز ولا لا  "
        return res


    def unlink(self):
        print('>>>>>>>',self) #"هيرجعلي الريكورد اللي انا واقف بعمل حذف ليه"
        for rec in self:
            if rec.total_amount and rec.total_amount > 0 :
                raise ValidationError(_('You can not delete !! first pay %d please' %rec.total_amount))
        res = super(HospitalPrescription, self).unlink()
        print('>>>>>>>', res)  #will print boolean value if your records deleted from data base or not
        return res


    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        print('>>>>>>>',self) #"هيرجعلي الريكورد اللي انا واقف بعمل دوبليكيت منه"
        print('============',default) #"هيرجعلي dectionary فاضي لاني محطتش اي داتا لاي فيلد وهو بيعمل دوبليكيت "
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        print('============',default) #"هيرجعلي dectionary فيه قيمة ال name بالقيمه الجديده "

        res= super(HospitalPrescription, self).copy(default=default)
        print('>>>>>>>', res)  # "هيرجعلي الريكورد الجديد اللي اتكريت"
        # "وساعتها لو عايز اعمل اساين لقيمه فيلد هتبقي res.field = value"
        return res



    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.doctor_id = self.appointment_id.doctor_id

    @api.model
    def name_get(self):
        result = []
        for pers in self:
            # هنا بتعدل الاسم بالطريقة اللي تحبها
            name = f"{pers.name} - {pers.patient_id.name if pers.patient_id else 'No Specialty'}"
            result.append((pers.id, name))
        return result


    def magic_command(self):
        pass
        # [0 ,0, {}]
        # first way
        # self.env['hospital.prescription.line'].create({'medicine_id':3 , 'prescription_id':self.id})

        # second way
        # self.create({'prescription_line_ids' : [(0, 0, {'medicine_id':3 , 'qty':25}),
        #                                         (0, 0, {'medicine_id':1 , 'qty':15})]})
        # -------------------------------------------------------------------------------------------
        # [{1 , id , {}}]
        # first way
        # vals = {'prescription_line_ids' : []}
        # for line in self.prescription_line_ids:
        #     vals['prescription_line_ids'].append([1, line.id , {'medicine_id':3 , 'qty':25}])
        # self.write(vals)

        #second way
        # for line in self.prescription_line_ids:
        #     line.write({'medicine_id':3 , 'qty':25})

        # -------------------------------------------------------------------------------------------

        # يتم الجذف من الداتا بيز دائما
        # [{2 , id , 0}]
        # first way
        # self.write({'prescription_line_ids':[(2 , 3 , 0), (2 , 4 , 0)] })

        # second way
        #self.unlink(3)
        #self.unlink(4)

        # يتم الجذف مؤقتا من الريكورد فقط ولكن الريكورد ال اتمسح  لسه مكانه في التيبل
        # [{3 , id , 0}]
        # first way
        # self.write({'prescription_line_ids':[(3 , 3 , false), ( 3, 4 , false)] })
        # -----------------------------------------------------------------------------------
        #  الكوماند id,3 لو مسحت لاين من الريلاشن الوان تو ميني هيتمسج من الداتا بيز وهيختفي ال الموديل بتاعه
        # لكن ال id,4 لو مسحت لاين من الوان تو ميني ريليشن هيتمسح من شاشة الريكورد ده بس لكن هيفضل مكانه ف الموديل ولو اختارته تاني في اللاينز هيظهر تلقائي في شاشة الريكوردالاصليه
        # [{4 , id , 0}]
        # first way
        # self.write({'prescription_line_ids':[(4 , 3 , false)] })
        # -----------------------------------------------------------------------------------
        #  بستخدمه لو عايز امسح كل الريكوردات اللي مختارها في الريليشن الوان تو ميني ولكن هيظل مسح مؤقت يعني هيبقوا لسه موجودين في الموديل بتاعهم لكن هيتمسحوا من شاشة الركورد الرئيسي فقط
        # [{5 , 0 , 0}]
        # first way
        # self.write({'prescription_line_ids':[(5 , 0 , 0)] })


        # [{6 , 0 , ids}]
        # first way
        # ids=[3,4,5]
        # self.write({'many2many_field':[(6 , 0 , ids )] })



class PrescriptionLine(models.Model):
    _name = 'hospital.prescription.line'
    _description = 'Prescription Line'


    prescription_id = fields.Many2one('hospital.prescription')
    medicine_id = fields.Many2one('hospital.medicine')
    stock_qty = fields.Integer(string="Stock Quantity",related="medicine_id.stock_qty")
    qty = fields.Integer(string="Quantity")
    instructions = fields.Text(string="Instructions")
    lines_count = fields.Integer(string="line Number")


    price_unit = fields.Float(string="Unit Price" ,related="medicine_id.price")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', related='user_id.company_id')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)



    price_subtotal =  fields.Monetary(string="Total Price",currency_field='currency_id',compute='_compute_price_subtotal')


    @api.model_create_multi
    def create(self, vals):
        for value in vals:
                medicine_id = self.env['hospital.medicine'].browse(value.get('medicine_id'))
                if value.get('medicine_id') and value.get('qty'):
                    if value.get('qty') <= medicine_id.stock_qty:
                        medicine_id.write({'stock_qty': medicine_id.stock_qty - value.get('qty')})
                    else:
                        raise ValidationError("Quantity Not Enough !!")
        return super(PrescriptionLine, self).create(vals)


    # (لو الكمية زادت → تخصم الفرق بس.  // لو الكمية قلت → ترجع الفرق للمخزون.  // لو ما اتغيرتش → ما يحصلش أي تعديل.)
    def write(self, vals):
        for rec in self:
            if 'qty' in vals and rec.medicine_id:
                new_qty = vals.get('qty')
                old_qty = rec.qty
                diff = new_qty - old_qty

                if diff > 0:  # محتاج يخصم زيادة
                    if rec.medicine_id.stock_qty >= diff:
                        rec.medicine_id.write({'stock_qty': rec.medicine_id.stock_qty - diff})
                    else:
                        raise ValidationError("Quantity Not Enough !!")
                elif diff < 0:  # رجع جزء من الكمية
                    rec.medicine_id.write({'stock_qty': rec.medicine_id.stock_qty + abs(diff)})

        return super(PrescriptionLine, self).write(vals)


    @api.depends('medicine_id','qty','medicine_id.price')
    def _compute_price_subtotal(self):
        for rec in self:
            if rec.medicine_id or rec.qty:
                rec.price_subtotal = rec.qty * rec.price_unit
            else:
                rec.price_subtotal = 0





