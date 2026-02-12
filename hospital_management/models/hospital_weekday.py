from odoo import models, fields

class HospitalWeekday(models.Model):
    _name = 'hospital.weekday'
    _description = 'WeekDay'

    name = fields.Char(string='Name')



