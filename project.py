from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, AccessError


class Project(models.Model):
    _inherit="project.project"

    project_code = fields.Char(string="Project Code")
    project_functional_sequence_code = fields.Char(string="Project Sequence Code")
    project_implementation_sequence_code = fields.Char(string="Project Sequence Code")

    def create_sequence(self):
        model = self.env['ir.sequence']
        if self.project_functional_sequence_code:
            model.create({
                'name': self.name+" "+"functional sequence",
                'implementation': 'standard',
                'code': self.project_functional_sequence_code,
                'active': True,
                'prefix':self.project_code+'|FUN|-',
                'padding': 5,
                'number_increment':1,
                'number_next_actual': 1
            })

        if self.project_implementation_sequence_code:
            model.create({
                'name': self.name + " " + "implementation sequence",
                'implementation': 'standard',
                'code': self.project_implementation_sequence_code,
                'active': True,
                'prefix': self.project_code + '|IMP|-',
                'padding': 5,
                'number_increment': 1,
                'number_next_actual': 1
            })

    @api.onchange('name')
    def update_sequence_info(self):
        project_code = None
        functional_code = 'fun'
        implementation_code = 'imp'
        name = self.name
        name_list = name.split(" ")
        for word in name_list:
            if not project_code:
                project_code = word[0].upper()
            else:
                project_code = project_code+word[0].upper()
            functional_code = functional_code+'.'+word.lower()
            implementation_code = implementation_code+'.'+word.lower()

        self.project_code = project_code
        self.project_functional_sequence_code= functional_code
        self.project_implementation_sequence_code = implementation_code


class Task(models.Model):
    _inherit ='project.task'

    task_category = fields.Selection([('fun', 'Functional'), ('imp', 'Implementation')],
                                     string='Category',
                                     required=True)
    @api.model
    def create(self, values):
        res = super(Task, self).create(values)
        if res.project_id:
            project = self.env['project.project'].browse(res.project_id.id)
        sequence = False
        if values.get('task_category') == 'fun':
            sequence = self.env['ir.sequence'].next_by_code(project.project_functional_sequence_code) or _('New')
        if values.get('task_category') == 'imp':
            sequence = self.env['ir.sequence'].next_by_code(project.project_implementation_sequence_code) or _('New')
        if sequence is not False:
            res.name = sequence +' '+ values['name']
        
        return res