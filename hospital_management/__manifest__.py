{

    'name': 'Hospital Management',
    'description': 'module managed by ahmed anwer',

    'author': 'ahmed anwer',
    'application': True,
    'sequence': 10,
    'depends': ['base', 'mail'],
    # 'depends' : ['report_xlsx'] ,
    'data': [
        'data/weekday_data.xml' ,
        'data/ir_sequence_data.xml' ,
        'security/hospital_security.xml' ,
        'security/ir.model.access.csv',
        'views/hospital_doctor_views.xml',
        'views/hospital_patient_views.xml',
        'views/hospital_prescription_views.xml' ,
        'views/hospital_appointment_views.xml' ,
        'views/hospital_medicine_views.xml' ,
        # 'views/res_config_settings_views.xml' ,
        'reports/prescription_report_template.xml' ,
        # 'reports/manager_xlsx_data.xml' ,
        #  'wizards/wizard_employee_view.xml' ,
        # 'wizards/wizard_employee_report_view.xml' ,
        'views/hospital_menus.xml',
    ],
    # 'demo':[
    #     'demo/demo_data.xml'
    # ]

}

# ترتيب فايلات ال xml في ال data مهم
# security =>data files => wizard => views =>menues
