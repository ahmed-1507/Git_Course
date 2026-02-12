from odoo import api, fields, models


class WizardEmployeeReport(models.TransientModel):
    _name = 'wizard.employee.report'
    _description = 'employee data report'


    lawyer_id = fields.Many2one('employee.office' , string='Name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ])

    # def print_employee_report(self):
    #     print("aaaaa" , self.read()[0])
    #     data = {
    #         'model':  'wizard.employee.report' ,
    #         'form_data' : self.read()[0]
    #     }
    #     print('data---->' , data)
    #     print("selected_employee_id=", data['form_data']['lawyer_id'][0])
    #     selected_employee_id= data['form_data']['lawyer_id'][0]
    #     selected_emp = self.env['employee.office'].search([('name','=',selected_employee_id)])
    #
    #     data['docs'] = selected_emp
    #     return self.env.ref('law_office.employee_data_report').report_action(self , data=data)

    def print_employee_report(self):
        print(self.read()[0] )
        data = {
            'model':  'wizard.employee.report' ,
            'form_data' : self.read()[0]
        }
        print(data)
        if data['form_data']['lawyer_id']:
            selected_employee_id = data['form_data']['lawyer_id'][0]
            selected_emp = self.env['employee.office'].search([('id', '=', selected_employee_id)])
            print(selected_emp)
        else:
            selected_emp = self.env['employee.office'].search([])

        employee_list = []
        for emp in selected_emp:
            vals = {
                'name': emp.name,
                'gender': emp.gender,
            }
            employee_list.append(vals)

        data['selected_emp'] = employee_list
        print("another data ",data)
        return self.env.ref('law_office.employee_data_report').report_action(self , data=data)

