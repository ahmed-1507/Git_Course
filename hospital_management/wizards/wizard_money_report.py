from odoo import api, fields, models


class WizardMoneyReport(models.TransientModel):
    _name = 'wizard.money.report'
    _description = 'money data report'


    manager_id = fields.Many2one('manager.office' , string='Manager')
    bill_date = fields.Datetime(default=fields.Datetime.now)
    description = fields.Text()

    def print_money_report(self):
        print(self.read()[0] )
        data = {
            'model' :'wizard.money.report' ,
            'form_data' : self.read()[0] ,

        }
        print(data)
        if data['form_data']['manager_id'] :
            selected_manager = data['form_data']['manager_id'][0]
            manager_report = self.env['money.safe'].search([('manager_id', '=', selected_manager)])
        # print(data['form_data']['manager_id'][0])
        else:
            manager_report = self.env['money.safe'].search([])

        manager_list = []
        for manager in manager_report:
            vals = {
                'manager_id' :manager.manager_id ,
                'bill_date' :manager.bill_date ,
                'description' :manager.description ,
            }
            manager_list.append(vals)
        data['manager_report'] = manager_list
        # print(docs)
        return self.env.ref('law_office.money_data_report').report_action(self , data=data)