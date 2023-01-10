from odoo import models, fields , api
from datetime import timedelta
from odoo .tools.translate import _
from odoo .exceptions import UserError
from odoo .exceptions import ValidationError
from odoo.tests.common import Form

class BaseArchive(models.Model):
    _name = 'base.archive'
    active = fields.Boolean(default=True)
    def do_archive(self):
        for record in self:
            record.active = not record.active

class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    is_public = fields.Boolean(groups='my_library.group_library_librarian')
    private_notes = fields.Text(groups='my_library.group_library_librarian')

    short_name = fields.Char(required = True)
    name = fields.Char('Title', required = True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many('res.partner', String='Authors')
    notes = fields.Text('Internal Notes')
    state = fields.Selection([('draft', 'Not available'),
                              ('available', 'Available'),
                              ('lost', 'Lost'),
                              ('borrowed', 'Borrowed')], default="draft")

    description = fields.Html('Decription')
    cover = fields.Binary('Book cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of pages')
    reader_rating = fields.Float('Reander Average Rating', digits=(14, 4),)

    age_days=fields.Float(string='Days Since Release', compute='_compute_age',inverse='_inverse_age',search='_search_age',store=False,compute_sudo=True)
    publisher_id = fields.Many2one('res.partner', string='Publisher', ondelete='set null', context={}, domain=[], )
    category_id = fields.Many2one('library.book.category')
    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')
    cost_price = fields.Float('Book Cost', digits='Book Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary(
        'Retail Price',
        # optional: currency_field = 'currency_id',
    )

    manager_remarks = fields.Text('Manager Remarks')
    isbn = fields.Char('ISBN')
    old_edition = fields.Many2one('library.book',string= 'Old Edition')

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days= book.age_days)
            book.date_release = d
    def _search_age(self, operator,value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        operator_map = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', }
        new_op = operator_map.get(operator, operator)
        return [('date_release',new_op,value_date)]

    _sql_constraints=[('name_uniq','UNIQUE(name)','Book title must be unique'),('positive_page','CHECK(pages>0)','No of pages must be positive')]
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name','=','message_ids')])
        return [(x.model,x.name) for x in models]

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result

    # @api.model
    # def is_allowed_transition(self, old_state, new_state):
    #     allowed=[('draft','available'),
    #              ('available','borrowed'),
    #              ('borrowed','available'),
    #              ('available','lost'),
    #              ('borrowed','lost'),
    #              ('lost','available')]
    #     return (old_state, new_state) in allowed
    # def change_state(self, new_state):
    #     for book in self:
    #         if book.is_allowed_transition(book.state,new_state):
    #             book.state = new_state
    #         else:
    #             msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
    #             raise UserError(msg)
    # def make_available(self):
    #     self.change_state('available')
    # def make_borrowed(self):
    #     self.change_state('borrowed')
    # def make_lost(self):
    #     self.change_state('lost')

    # chapter 8 start
    def make_available(self):
        self.ensure_one()
        self.state='available'
    def make_borrowed(self):
        self.ensure_one()
        self.state = 'borrowed'
    def make_lost(self):
        self.ensure_one()
        self.state= 'lost'
        if not self.env.context.get('avoid_deactivate'):
            self.active = False
    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.creat({
            'book_id':self.id,
            'borrower_id':self.env.user.partner_id.id,
        })
    # stop

    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("All Members:", all_members)
        return True

    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        record = self.env['library.book.category'].create(parent_category_val)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def find_book(self):
        domain = [
            '|', '&', ('name', 'ilike', 'Book Name'), ('category_id.name', 'ilike', 'Category Name'),
            '&', ('name', 'ilike', 'Book Name 2'), ('category_id.name', 'ilike', 'Category name 2')
        ]
        books = self.search(domain)
        print('Books found: %s', books)

    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.book_with_multiple_authors(all_books)
        print('Filtered Books: %s', filtered_books)

    @api.model
    def book_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)

    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        print('Books Authors: %s', books_authors)
    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    # def sort_books(self):
    #     all_books = self.search([])
    #     books_sorted = self.sort_books_by_date(all_books)
    #     print('Books after sorting: %s', books_sorted)
    # @api.model
    # def sort_books_by_date(self,all_books):
    #     return all_books.sorted(key='pages', reverse=False)

    # @api.model
    # def create(self, values):
    #     if not self.user_has_groups('mylibrary.acl_book_librarian'):
    #         if 'manager_remarks' in values:
    #             raise UserError(
    #                 'You are not allowed to modify'
    #                 'manager_remarks'
    #             )
    #     return super(LibraryBook, self) .create(values)
    #
    # @api.model
    # def write(self, vals):
    #     if not self.user_has_groups('mylibrary.acl_book_librarian'):
    #         if 'manager_remarks' in vals:
    #             raise UserError('You are not allowed to modify'
    #                 'manager_remarks')
    #     return super(LibraryBook, self).write(vals)

    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
        return result
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += {'|', '|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     }
        return super(LibraryBook, self)._name_search(name = name, args = args, operator=operator, limit= limit, name_get_uid=name_get_uid)

    @api.model
    def _update_book_price(self):
        all_books = self.search([])
        for book in all_books:
            book.cost_price += 10

    def average_book_occupation(self):
        self.flush()
        sql_query= """
        SELECT lb.name, avg((EXTRACT(epoch from age(return_date, rent_date))/86400))::int
        FROM library_book_rent AS lbr
        JOIN library_book AS lb ON lb.id = lbr.book_id
        WHERE lbr.state = 'returned'
        GROUP BY lb.name;"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        print("Average book occupation: %s", result)

    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.return.wizard']
        wizard.create({'borrower_id': self.env.user.partner_id.id}).books_returns()

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _oder = 'name'
    published_book_ids = fields.One2many('library.book','publisher_id',string='Published Book')
    authored_book_ids = fields.Many2many('library.book',string='Authored Books',)
    count_books = fields.Integer('Number of authored Book',compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_book(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)

class LibraryMember(models.Model):
    _name = "library.member"
    _inherits = {'res.partner':'partner_id'}
    _description = 'Library Member'
    partner_id = fields.Many2one('res.partner',ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date Of Birth')