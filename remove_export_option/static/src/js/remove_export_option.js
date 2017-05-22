/*
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
*/
openerp.remove_export_option = function(instance) {

    var _t = instance.web._t;
    var SUPERUSER_ID = 1;

    instance.web.Sidebar.include({
        add_items: function(section_code, items) {
            var self = this;
            var _super = this._super.bind(this);
            // allow Export for admin user
            var Users = new instance.web.Model('res.users');
            Users.call('has_group', ['remove_export_option.group_hide_export']).done(function(is_export) {
                if (! is_export) {
                    var export_label = _t("Export");
                    if (section_code == 'other') {
                        for (var i = 0; i < items.length; i++) {
                            if (items[i]['label'] == export_label) {
                                items.splice(i, 1)
                            }
                        }
                    }
                }
                if (items.length > 0) {
                    _super(section_code, items);
                }
            });
        },

    });

};
