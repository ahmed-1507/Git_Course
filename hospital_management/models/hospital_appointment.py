from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment'
    _rec_name = 'doctor_id'
    # _order = 'sequence , id'
    #  _log_access=False  ==> means that [create_date , create_uid , write_date , write_uid] will not be created as a default like any table
    #  باقي ال attributes موجوده في فايل models بتاع اودوو BaseModel class

    doctor_id = fields.Many2one('hospital.doctor')
    patient_id = fields.Many2one('hospital.patient' ,required= True)
    start_time = fields.Datetime(default=fields.Datetime.now,string="Start Date")
    end_time = fields.Datetime(string="End Date" ,compute='_compute_end_time')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft')
    notes = fields.Text()
    ref = fields.Char(string="Reference", copy=False, readonly=True,
                      default=lambda self: ('New'))

    active = fields.Boolean('Activ',default=True)  # to make an archive button
    progress=fields.Integer(string='progress' , compute='_compute_progress')
    is_today_appointment = fields.Boolean(string='is today', compute='_compute_is_today_appointment')
    app_no = fields.Integer(string="APP NO")

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft' :
                progress = 25
            elif rec.state == 'confirmed' :
                progress = 50
            elif rec.state == 'done' :
                progress = 100
            else:
                progress = 0
            rec.progress = progress


    @api.model
    def default_get(self, fields):
        print(">>>>>>>>fffff",fields)  # will return all this model fields names but in list
        result = super(HospitalAppointment, self).default_get(fields)
        print((result))  # "هيرجعلي في dectionary كل الفيلدات اللي واخده ال attripute بتاع default =value  في الفيلد بتاعها "
        # "ولو مفيش ولا فيلد واخد default value يبقي هترجعلي empty dectionary "
        result['ref'] = 'Appointment from default_get()'
        print(">>>>>>>>rrrrr",result)  # "هترجعلي dectionary فيه الفيلدات اللي عملتلها  default value زي ال description وغيره بقي"
        return result


    @api.depends('start_time','patient_id')
    def _compute_end_time(self):
        for rec in self:
            if rec.start_time:
                rec.end_time = rec.start_time + timedelta(minutes=30)
            else:
                rec.end_time = False

    # computed fields by default are non stored so that we can't search about this field and put it in search view
    # and if you want to put this computed field in search view ou must make  store=True

    @api.depends('start_time')
    def _compute_is_today_appointment(self):
        print("from compute_is_today_appointment")
        for rec in self:
            is_today_app = False      #القيمه دي متغير عادي مش فيلد
            today = date.today()
            if rec.start_time:
                if today.day == rec.start_time.day and today.month == rec.start_time.month:
                    is_today_app = True
                rec.is_today_appointment = is_today_app   #ا هنعمل اساين المتغير للفيلد بقي
            else:
                rec.is_today_appointment=False

    @api.constrains('doctor_id', 'start_time','patient_id','end_time')
    def _check_appointment_overlap(self):
        for rec in self:
            # Doctor overlap
            if rec.doctor_id and rec.start_time:
                # ممنوع حجزين في نفس الوقت
                conflict = rec.search([
                    ('id', '!=', rec.id),
                    ('doctor_id', '=', rec.doctor_id.id),
                    ('start_time', '=', rec.start_time),
                ])
                if conflict:
                    raise ValidationError("This doctor already has an appointment at this time!")

            # ممنوع حجز في يوم مش موجود ضمن available_days
            if rec.start_time:
                appointment_day = rec.start_time.strftime('%A')
                print(">>>>>>>>>>>>>>>",rec.start_time.strftime('%A'))
                print("==============>",rec.doctor_id.available_days_ids.mapped('name'))
                if appointment_day not in rec.doctor_id.available_days_ids.mapped('name'):
                    raise ValidationError(f"Doctor %s  is not available on {appointment_day}." %(rec.doctor_id.name))

            if rec.doctor_id:
                doctor_records = self.search([
                    ('id', '!=', rec.id),
                    ('doctor_id', '=', rec.doctor_id.id)
                ])
                for record in doctor_records:
                    if record.start_time < rec.end_time and record.end_time > rec.start_time:
                        raise ValidationError("This doctor already has an appointment at this time!")

            # Patient overlap (مع أي دكتور)
            if rec.patient_id:
                patient_records = self.search([
                    ('id', '!=', rec.id),
                    ('patient_id', '=', rec.patient_id.id),
                ])
                for record in patient_records:
                    if record.start_time < rec.end_time and record.end_time > rec.start_time:
                        raise ValidationError("This patient already has an appointment at this time!")



    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }    # put it under a function  to reload a page automatically after action


    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            self.env['mail.message'].create({
                'model': 'hospital.appointment',
                'res_id': rec.id,
                'message_type': 'notification',
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'body': f"You have a new confirmed appointment with {rec.patient_id.name} on {rec.start_time.strftime('%Y-%m-%d %H:%M')}.",
                'partner_ids': [(6, 0, [rec.doctor_id.user_id.partner_id.id])],
            })
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Confirmed !',
                    'type': 'rainbow_man',
                }
            }



    def action_done(self):
        for rec in self:
            rec.state = 'done'
            action = self.env.ref('hospital_management.hospital_patient_view_action')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'click to open Patient %s' %rec.patient_id.name,
                    'message': '%s',
                    'links': [{
                        'label': rec.patient_id.name,
                        'url':f'#action={action.id}&model=hospital.patient&view_type=form&id={rec.patient_id.id}'
                    }],
                    'sticky': False,
                }  }


    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Cancelled successfully',
                    'type': 'danger',
                    'sticky': False,
                }
            }
            # type ==> the color of the popup
            # sticky = true   ==> معناها مش البو اب مش هيختفي تلقائي لازم انا اقفله او ارستر الصفحه


    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError(_('You can not delete an confirmed appointment %s' %rec.patient_id.id))
        return super(HospitalAppointment, self).unlink()


    def print_method(self):
        doctor_obj = self.env['hospital.doctor']
        doctor_ids = doctor_obj.search([])
        doctor_counts = doctor_obj.search_count([])
        print(">>>>>>doctor_counts",doctor_counts)
        # you can use these attributes with search      .search([] , limit=5 ,offset=20, order='id'or'name'or any field)


        #لحد دلوقتي مش فاهم ال browse بتعمل ايه
        doctor_record =  doctor_obj.browse(doctor_ids)
        print("doctor_record",doctor_record)


        searched_doctors = doctor_obj.search([('age', '>',26)])
        for doctor in searched_doctors:
            doctor.name = 'Ahmed mazon'
        # search(domain) == filtered(domain)   هي هي هتدي نفس النتيجة بالظبط
        filtered_doctors = doctor_obj.search([]).filtered(lambda a: a.age > 26)
        for doctor in filtered_doctors:
            doctor.name = 'Ahmed mazon'


        mapped_doctors = doctor_obj.search([]).mapped('name')
        # or
        # mapped_doctors = doctor_obj.search([]).mapped(lambda n: n.name)
        print('mapped_doctors ----->', mapped_doctors)
        for rec in mapped_doctors:
            print('loooop ----->' ,rec)

        sorted_doctors = doctor_obj.search([]).sorted('age')
        # sorted_doctors = doctor_obj.search([]).sorted(lambda a: a.age)
        print("sorted_doctors",sorted_doctors)
        for rec in sorted_doctors:
            print(">>>>>>>>>>>>",rec.name)
            rec.name = "deco"






