import base64
import io

from odoo import models

class ManagerDataXlsx(models.AbstractModel):
    _name = 'report.law_office.manager_xlsx_documents'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, managers):

        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True , 'align':'center' , 'bg_color':'yellow'})

        for obj in managers:
            #-------------------------------
            # لو عايزهم كلهم في صفحه واحده هنقل الاربعه دول قبل ال loop
            sheet = workbook.add_worksheet(obj.name)
            sheet.set_column('C:E', 15)
            row = 2
            col = 2
            #-------------------------------

            row += 1
            sheet.merge_range(row, col, row, col+1 , 'ID Card' , format_1)

            row += 1
            if obj.image:
                manager_image = io.BytesIO(base64.b64decode(obj.image))
                sheet.insert_image(row, col, "image.png" , {'image_data':manager_image , 'x_scale':0.5 , 'y_scale' :0.5})

            row += 6
            sheet.write(row, col, 'Name', bold)
            sheet.write(row, col + 1, obj.name)
            row += 1
            sheet.write(row, col, 'Age', bold)
            sheet.write(row, col + 1, obj.age)
            row += 1
            sheet.write(row, col, 'Country', bold)
            sheet.write(row, col + 1, obj.country)

            row += 2
