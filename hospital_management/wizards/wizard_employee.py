from odoo import models,fields,api

class Wizard_employee(models.TransientModel):

    _name = 'wizard.employee'


    # if you need to put a default value to a field in popup wizard by python func
    @api.model
    def default_get(self, fields):
        result = super(Wizard_employee, self).default_get(fields)
        if self.env.context.get('active_id'):
            print((fields))
            print('aaaaaaaaaaaaaa', (result))
            print('................ ', self.env.context.get('active_id'))
            result['manager'] = self.env['manager.office'].browse(self._context.get('active_id')).name
        return result



    name = fields.Char()
    is_accepted = fields.Boolean()
    salary = fields.Float(digits=(6,2))
    employee_id = fields.Many2one('employee.office' , ondelete='restrict')


    def Save_employee_values(self):
        self.env['employee.office'].create({
            'name' : self.name ,
            'is_accepted' : self.is_accepted ,
            'salary' : self.salary })


    def update_employee_name(self):
        result = self.env['employee.office'].browse(self._context.get('active_ids')).update({'employee_idd' : self.employee_id})
        return result














