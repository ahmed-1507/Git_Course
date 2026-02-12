from odoo import api, fields, models


class PrescriptionReport(models.AbstractModel):
    _name = 'report.hospital_management.prescription_report_template'      #report.module_name.template_id
    _description = 'prescription report'




    @api.model
    def _get_report_values(self, docids, data=None):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>self", self)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>docids", docids)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>data", data)

        docs = self.env['hospital.prescription'].browse(docids[0])
        prescription_ids = self.env['hospital.prescription'].search([('patient_id', '=', docs.patient_id.id)])
        prescription_list = []
        for pr in prescription_ids:
            vals = {
                'name': pr.name,
                'appointment_id': pr.appointment_id.patient_id.name,
            }
            prescription_list.append(vals)
            print("lllllllllllllllllllllllllllllllllll",prescription_list)
        return {
            'doc_model': 'hospital.prescription',
            'data': data,
            'doc_ids': self.ids,
            'docs': docs,
            'prescription_list': prescription_list,
        }




    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     print('doneeeeeeeeeeeeeeeeeeeeeee', data)
    #     # lawyer_id = data.get('form_data').get('name')
    #     gender = data.get('form_data').get('gender')
    #     age = data.get('form_data').get('age')
    #     domain = []
    #     if lawyer_id:
    #         name_id = data.get('form_data').get('lawyer_id')[1]
    #         domain += [(lawyer_id, '=', name_id)]
    #
    #     if gender:
    #         domain += [('gender', '=', gender)]
    #
    #     if age != 0:
    #         domain += [('age', '=', age)]
    #
    #     else:
    #         domain = [(1, '=', 1)]
    #
    #     docs = self.env['employee.office'].search(domain)
    #
    #     return {
    #         'doc_model': 'wizard.employee.report',
    #         'data': data,
    #         # 'doc_ids': self.ids,
    #         'docs': docs,
    #         'email': 'ahmed@gmail.com'
    #     }


    #
    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     if not data:
    #         data = {}
    #     if "company_id" not in data:
    #         wiz = self.env["activity.statement.wizard"].with_context(
    #             active_ids=docids, model="res.partner"
    #         )
    #         data.update(wiz.create({})._prepare_statement())
    #     data["amount_field"] = "amount"
    #     return super()._get_report_values(docids, data)



