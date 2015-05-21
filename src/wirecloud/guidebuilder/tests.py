# -*- coding: utf-8 -*-

# Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import os
import time

from django.conf import settings
import shutil

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from wirecloud.commons.utils.testcases import uses_extra_resources, WirecloudSeleniumTestCase, wirecloud_selenium_test_case, DynamicWebServer, LocalFileSystemServer

__test__ = 'wirecloud.guidebuilder' in settings.INSTALLED_APPS

if __test__ is True:
    from PIL import Image

if __test__ and not os.path.exists(os.path.join(settings.BASEDIR, 'screens')):
    os.mkdir(os.path.join(settings.BASEDIR, 'screens'))

list_resources = ['CoNWeT_simple-history-module2linear-graph_2.3.2.wgt',
                  'CoNWeT_ngsi-source_3.0.2.wgt',
                  'CoNWeT_ngsientity2poi_3.0.3.wgt',
                  'CoNWeT_linear-graph_3.0.0b3.wgt',
                  'CoNWeT_map-viewer_2.5.3.wgt']
# Common functions


def image_path(name='Wirecloud_UG.png', extra=None, resource=False):
    if extra is not None:
        name = name if not name.endswith('.png') else name[:-4]
        name = '{}_{}.png'.format(name, extra)
    name = name if name.endswith('.png') else "{}.png".format(name)
    if not resource:
        basepath = os.path.join(settings.BASEDIR, 'screens')
    else:
        basepath = os.path.join(os.path.dirname(__file__), 'resources')
    return os.path.join(basepath, name)


def take_capture(driver, name='Wirecloud_UG.png', extra=None):
    path = image_path(name, extra)
    driver.save_screenshot(path)
    return path


def merge_images(img1, img2, position):
    img1.paste(img2, position, img2)


def add_image(imgp, position, imagename):
    lp = image_path(os.path.join('resources', imagename), resource=True)
    base = Image.open(imgp)
    l = Image.open(lp)
    merge_images(base, l, position)
    base.save(imgp)


def add_market_list(imgp, position):
    add_image(imgp, position, 'marketlist.png')


def add_pointer(imgp, position, pointer=True):
    mousefn = 'select_l.png' if pointer else 'arrow_l.png'
    mousefn = os.path.join('mouse', mousefn)
    mousep = image_path(os.path.join('resources', mousefn, resource=True))
    base = Image.open(imgp)
    mouse = Image.open(mousep)
    base.paste(mouse, position, mouse)
    base.save(imgp)


def crop_image(imgp, left=0, upper=0, right=None, lower=None):
    image = Image.open(imgp)
    w, h = image.size
    right = right if right is not None else w
    lower = lower if lower is not None else h
    image.crop((left, upper, right, lower)).save(imgp)


def crop_down(imgp, widg, offs=10):
    lower_cut = get_position(widg, 1.0, 1.0)[1] + offs
    crop_image(imgp, lower=lower_cut)


def get_position(widg, xoff=0.75, yoff=0.75):
    return (widg.location['x'] + int(xoff * widg.size['width']),
            widg.location['y'] + int(yoff * widg.size['height']))


def create_box(widg, offs=3):
    return (widg.location['x'] - offs,
            widg.location['y'] - offs,
            widg.location['x'] + widg.size['width'] + offs,
            widg.location['y'] + widg.size['height'] + offs)


def get_by_condition(driver, css, f):
    for d in driver.find_elements_by_css_selector(css):
        if f(d):
            return d
    return None


def get_by_text(driver, css, text):
    return get_by_condition(driver, css, lambda x: x.text == text)


def get_by_contains(driver, css, text):
    return get_by_condition(driver, css, lambda x: text in x.text)


def get_first_displayed(driver, css):
    return get_by_condition(driver, css, lambda x: x.is_displayed())


def get_anchors(w1, w2, label1, label2):
    froml = get_by_text(w1, '.labelDiv', label1)
    tol = get_by_text(w2, '.labelDiv', label2)
    fromc = froml.find_element_by_css_selector('.anchor.icon-circle')
    toc = tol.find_element_by_css_selector('.anchor.icon-circle')
    return (fromc, toc)


def connect_anchors(driver, w1, w2, label1, label2):
    fromc, toc = get_anchors(w1, w2, label1, label2)
    ActionChains(driver).drag_and_drop(fromc, toc).perform()


def move_elem(driver, elem, x, y):
    ActionChains(driver).click_and_hold(
        elem).move_by_offset(x, y).release().perform()


def read_response_file(*response):
    f = open(market_path_base(*response))
    contents = f.read()
    f.close()
    return contents


def market_path_base(*args):
    return os.path.join(os.path.dirname(__file__), 'test-data', *args)


@wirecloud_selenium_test_case
class BasicSeleniumGuideTests(WirecloudSeleniumTestCase):
    fixtures = ('initial_data', 'selenium_test_data', 'guide_test_data')
    servers = {
        'http': {
            'marketplace.example.com': DynamicWebServer(),
            'repository.example.com': LocalFileSystemServer(market_path_base('responses', 'repository')),
            'static.example.com': LocalFileSystemServer(market_path_base('responses', 'static')),
            'store.example.com': DynamicWebServer(fallback=LocalFileSystemServer(market_path_base('responses', 'store'))),
            'store2.example.com': DynamicWebServer(fallback=LocalFileSystemServer(market_path_base('responses', 'store2')))
        },
    }

    tags = ('wirecloud-guide',)

    def setUp(self):
        self.store_list_response = read_response_file(
            'responses', 'marketplace', 'store_list.xml')
        self.store1_offerings = read_response_file(
            'responses', 'marketplace', 'store1_offerings.xml')
        self.store2_offerings = read_response_file(
            'responses', 'marketplace', 'store2_offerings.xml')
        super(BasicSeleniumGuideTests, self).setUp()

        self.network._servers['http']['marketplace.example.com'].clear()
        self.network._servers['http']['marketplace.example.com'].add_response(
            'GET', '/registration/stores/', {'content': self.store_list_response})
        self.network._servers['http']['marketplace.example.com'].add_response(
            'GET', '/offering/store/FIWARE%20Lab/offerings', {'content': self.store1_offerings})
        self.network._servers['http']['marketplace.example.com'].add_response(
            'GET', '/offering/store/FIWARE/offerings', {'content': self.store2_offerings})

    def configure_ngsi_source(self, source):
        source.find_element_by_css_selector('.icon-cog').click()
        get_by_text(self.driver.find_element_by_css_selector(
            '.se-popup-menu.se-popup-menu-bottom-left'), '.se-popup-menu-item', 'Settings').click()
        dialog = get_first_displayed(self.driver, '.window_menu')
        self.fill_form_input(dialog.find_element_by_css_selector('input[name="ngsi_server"]'),
                             'http://orion.lab.fiware.org:1026/')
        self.fill_form_input(dialog.find_element_by_css_selector('input[name="ngsi_proxy"]'),
                             'https://ngsiproxy.lab.fiware.org')
        self.fill_form_input(dialog.find_element_by_css_selector('input[name="ngsi_entities"]'),
                             'Node, AMMS, Regulator')
        self.fill_form_input(dialog.find_element_by_css_selector(
            'input[name="ngsi_update_attributes"]'), 'Latitud, Longitud, presence, batteryCharge, illuminance, ActivePower, ReactivePower, electricPotential, electricalCurrent')
        dialog.find_element_by_css_selector('.btn-primary').click()

    def configure_ngsi_entity(self, source):
        source.find_element_by_css_selector('.icon-cog').click()
        get_by_text(self.driver.find_element_by_css_selector(
            '.se-popup-menu.se-popup-menu-bottom-left'), '.se-popup-menu-item', 'Settings').click()
        dialog = get_first_displayed(self.driver, '.window_menu')
        self.fill_form_input(dialog.find_element_by_css_selector('input[name="coordinates_attr"]'),
                             'Latitud, Longitud')
        dialog.find_element_by_css_selector('.btn-primary').click()

    @uses_extra_resources(list_resources)
    def test_creating_new_workspace(self):
        # Inicializacion
        # La altura usa la barra de tareas
        self.driver.set_window_size(1024, 768)
        self.login()
        self.create_workspace('My Multimedia Workspace')
        self.create_workspace('Issue Trouble')
        self.open_menu().click_entry('Workspace')
        self.wait_wirecloud_ready()

        menu_widg = self.driver.find_element_by_css_selector(
            '.wirecloud_header_nav .icon-reorder')

        # Captura escritorio inicial
        imgp = take_capture(self.driver, extra=1)
        crop_down(
            imgp, self.driver.find_element_by_css_selector('.emptyWorkspaceInfoBox'))

        # Capturar la lista de workspaces
        menu = self.open_menu()
        imgp = take_capture(self.driver, extra=3)
        add_pointer(imgp, get_position(menu_widg))  # Add the mouse
        crop_down(imgp, menu.element)  # Crop down the image

        # Capturar new workspace
        newworkspace_menu = menu.get_entry('New workspace')
        ActionChains(self.driver).move_to_element(newworkspace_menu).perform()
        imgp = take_capture(self.driver, extra=4)
        add_pointer(imgp, get_position(newworkspace_menu, 0.8, 0.5))
        crop_down(imgp, menu.element)  # Crop down the image

        # Capture writing new workspace name
        newworkspace_menu.click()
        dialog = self.driver.find_element_by_css_selector(
            '.window_menu.new_workspace')
        self.fill_form_input(dialog.find_element_by_css_selector('input[name="name"]'),
                             'History Info')
        imgp = take_capture(self.driver, extra=5)
        crop_image(imgp, *create_box(dialog))

        # Wait complete and capture state
        # dialog.find_element_by_xpath("//*[text()='Accept']").click()
        dialog.find_element_by_css_selector(
            'button.btn-primary.styled_button').click()
        self.wait_wirecloud_ready()
        imgp = take_capture(self.driver, extra='HistoryInfoWorkspace')
        crop_down(
            imgp, self.driver.find_element_by_css_selector('.emptyWorkspaceInfoBox'))

        btn = self.driver.find_element_by_css_selector(
            '.wirecloud_toolbar .icon-shopping-cart')
        ActionChains(self.driver).move_to_element(btn).perform()
        time.sleep(0.2)
        imgp = take_capture(self.driver, extra=17)
        add_pointer(imgp, get_position(btn, 0.8, 0.5))
        crop_down(
            imgp, self.driver.find_element_by_css_selector('.emptyWorkspaceInfoBox'))

        # Workspace Settings
        self.open_menu().click_entry('Settings')
        dialog = self.driver.find_element_by_css_selector(
            '.window_menu.workspace_preferences')
        imgp = take_capture(self.driver, extra='WorkspaceSettings')
        crop_image(imgp, *create_box(dialog))

    @uses_extra_resources(list_resources)
    def test_browsing_marketplace(self):
        # La altura usa la barra de tareas
        self.driver.set_window_size(1024, 768)
        self.login()

        with self.marketplace_view as marketplace:
            marketplace.switch_to('origin')
            marketplace.delete()
            marketplace.switch_to('FIWARE Lab')
            select = self.driver.find_element_by_css_selector(
                '.se-select select')

            # Market list screenshot
            imgp = take_capture(
                self.driver, 'Wirecloud_Marketplace_plus_stores.png')
            add_market_list(imgp, get_position(select, 0.0, 1.0))
            add_pointer(imgp, get_position(select, 0.7, 2.3), False)
            crop_down(imgp, select, 80)

            # marketplaces screenshot
            popup_menu = marketplace.open_menu()
            m_menu = popup_menu.get_entry('FIWARE Lab')
            ActionChains(self.driver).move_to_element(m_menu).perform()
            imgp = take_capture(self.driver, extra=8)
            add_pointer(imgp, get_position(m_menu, 0.8, 0.5))
            crop_down(imgp, popup_menu.element, 80)

            # Copy the previous to other one that uses it after
            shutil.copy2(imgp, image_path(extra=10))

            # Add marketplace
            m_menu = popup_menu.get_entry('Add new marketplace')
            ActionChains(self.driver).move_to_element(m_menu).perform()
            imgp = take_capture(self.driver, extra='AddNewMarketplace')
            add_pointer(imgp, get_position(m_menu, 0.8, 0.5))
            crop_down(imgp, popup_menu.element, 80)

            # Adding marketplace
            m_menu.click()
            dialog = self.driver.find_elements_by_css_selector(
                '.window_menu')[1]
            self.fill_form_input(dialog.find_element_by_css_selector('input[name="name"]'),
                                 'FIWARE')
            self.fill_form_input(dialog.find_element_by_css_selector('input[name="url"]'),
                                 'http://repository.example.com')
            Select(dialog.find_element_by_css_selector(
                'select')).select_by_index(1)
            imgp = take_capture(self.driver, extra='AddingFiwareMarketplace')
            crop_image(imgp, *create_box(dialog))

            # After added the new marketplace
            button = dialog.find_element_by_css_selector(
                'button.btn-primary.styled_button')
            button.click()
            self.wait_wirecloud_ready()
            # imgp = take_capture(self.driver, extra=9)

            marketplace.switch_to('FIWARE Lab')
            # Where are my resources
            btn = self.driver.find_element_by_css_selector(
                '.wirecloud_toolbar .icon-archive')
            ActionChains(self.driver).move_to_element(btn).perform()
            time.sleep(0.2)
            imgp = take_capture(self.driver, "Wirecloud_switch_to_local")
            add_pointer(imgp, get_position(btn, 0.8, 0.5))
            crop_down(imgp, select, 80)

        with self.myresources_view as myresources:
            # Resources
            self.clean_resources(myresources)
            imgp = take_capture(self.driver, extra=9)

            btn = self.driver.find_element_by_css_selector(
                '.wirecloud_toolbar .icon-cloud-upload')
            # Where are upload button
            ActionChains(self.driver).move_to_element(btn).perform()
            imgp = take_capture(self.driver, extra="UploadButton")
            add_pointer(imgp, get_position(btn, 0.5, 0.5))

            # Upload dialog
            btn.click()
            dialog = self.driver.find_element_by_css_selector(
                '.window_menu.wc-upload-mac-dialog.wc-upload-mac-dialog-empty')
            imgp = take_capture(self.driver, extra='uploadNew')
            crop_image(imgp, *create_box(dialog))
            dialog.find_element_by_css_selector(
                '.btn-default.styled_button').click()  # cancel

            # Click in a widget for details
            container = get_first_displayed(
                self.driver, '.se-container.resource_list')
            widg = get_by_contains(
                container, '.resource.click_for_details', 'widget')
            # widg = container.find_element_by_css_selector('.resource.click_for_details')
            ActionChains(self.driver).move_to_element(widg).perform()
            imgp = take_capture(self.driver, 'Wirecloud_open_details')
            add_pointer(imgp, get_position(widg, 0.5, 0.5))
            crop_down(imgp, widg, 50)

            # Publish button
            widg.click()
            time.sleep(0.2)
            container = get_first_displayed(
                self.driver, '.advanced_operations')
            btn = get_by_text(container, '.styled_button', 'Publish')
            ActionChains(self.driver).move_to_element(btn).perform()  # wait?
            imgp = take_capture(self.driver, "Wirecloud_click_publish")
            add_pointer(imgp, get_position(btn, 0.8, 0.8))

            # Publish dialog
            btn.click()
            dialog = self.driver.find_element_by_css_selector(
                '.window_menu.publish_resource')
            dialog.find_element_by_css_selector(
                'input[value="admin/FIWARE Lab"]').click()
            select = dialog.find_element_by_css_selector('.se-select select')
            imgp = take_capture(
                self.driver, 'Wirecloud_publish_resource_store_select')
            add_market_list(imgp, get_position(select, 0.0, 1.0))
            add_pointer(imgp, get_position(select, 0.7, 2.3), False)

            get_by_text(dialog, 'button', 'Cancel').click()
            self.driver.find_element_by_css_selector(
                '.wirecloud_header_nav .btn-large .icon-caret-left').click()
    test_browsing_marketplace.tags = ('wirecloud-guide', 'ui-marketplace')

    @uses_extra_resources(list_resources)
    def test_building_mashup(self):
        # La altura usa la barra de tareas
        self.driver.set_window_size(1024, 768)
        self.login()
        self.create_workspace('History Info')
        self.open_menu().click_entry('History Info')

        with self.myresources_view as resources:
            # Remove old
            self.clean_resources(resources)

            # Add to workspace(1)
            container = get_first_displayed(
                self.driver, '.se-container.resource_list')
            widg = get_by_contains(
                container, '.resource.click_for_details', 'Linear Graph')
            ActionChains(self.driver).move_to_element(widg).perform()
            imgp = take_capture(self.driver, extra='20_1')
            add_pointer(imgp, get_position(widg, 0.5, 0.5))
            crop_down(imgp, widg, 50)

            # Add to workspace(2)
            widg.click()
            time.sleep(0.2)
            container = get_first_displayed(
                self.driver, '.advanced_operations')
            btn = get_by_text(container, '.styled_button', 'Add to workspace')
            ActionChains(self.driver).move_to_element(btn).perform()  # wait?
            imgp = take_capture(self.driver, extra="20_2")
            add_pointer(imgp, get_position(btn, 0.8, 0.8))

            btn.click()  # Add the widget Linear Graph
            time.sleep(0.5)

            widg = get_by_contains(
                self.driver, '.fade.iwidget.in', 'Linear Graph')
            dragc = widg.find_element_by_css_selector('.rightResizeHandle')
            # pos = get_position(dragc, 1.0, 1.0)
            # referent_y = pos[1]
            move_elem(self.driver, dragc, 450, 337)
            # Resize the widget?
            # get the widget and crop down
            imgp = take_capture(self.driver, extra=21)
            widg = get_by_contains(
                self.driver, '.fade.iwidget.in', 'Linear Graph')
            crop_down(imgp, widg)

            self.driver.find_element_by_css_selector(
                '.wirecloud_toolbar .icon-archive').click()
            time.sleep(0.2)
            self.driver.find_element_by_css_selector(
                '.wirecloud_header_nav .btn-large .icon-caret-left').click()
            time.sleep(0.2)
            get_by_contains(
                self.driver, '.resource.click_for_details', 'Map Viewer').click()
            get_by_text(
                self.driver, '.styled_button', 'Add to workspace').click()
            time.sleep(0.5)

            # Resize the widget?
            widg = get_by_contains(
                self.driver, '.fade.iwidget.in', 'Map Viewer')
            dragc = widg.find_element_by_css_selector('.bottomResizeHandle')
            pos = get_position(dragc, 1.0, 1.0)
            ActionChains(self.driver).click(dragc).click_and_hold(
                dragc).move_by_offset(30, 1030).release().perform()
            # move_elem(self.driver, dragc, 420, 420)
            # get the widget and crop down
            imgp = take_capture(self.driver, extra=22)
            widg = get_by_contains(
                self.driver, '.fade.iwidget.in', 'Map Viewer')

            widg_menu = widg.find_element_by_css_selector('.widget_menu')
            setts_btn = widg_menu.find_element_by_css_selector(
                '.buttons .icon-cogs')
            ActionChains(self.driver).move_to_element(setts_btn).perform()
            time.sleep(0.2)

            # get the widget and crop down
            imgp = take_capture(self.driver, extra=23)
            box = create_box(widg_menu, 40)
            box = (box[0] + 37, box[1] + 37, box[2] - 37, box[3])
            add_pointer(imgp, get_position(setts_btn, 0.5, 0.5))
            crop_image(imgp, *box)

            setts_btn.click()
            menu = self.driver.find_element_by_css_selector(
                '.se-popup-menu.se-popup-menu-bottom-left')
            btn = get_by_contains(menu, '.se-popup-menu-item', 'Settings')
            ActionChains(self.driver).move_to_element(btn).perform()
            # get the widget and crop down
            imgp = take_capture(self.driver, extra=24)
            box = create_box(menu, 130)
            box = (box[0], box[1], box[2] + 100, box[3] + 100)
            add_pointer(imgp, get_position(btn))
            crop_image(imgp, *box)

            btn.click()
            dialog = get_first_displayed(self.driver, '.window_menu')
            self.fill_form_input(dialog.find_element_by_css_selector(
                'input[name="centerPreference"]'), 'Santander')
            # self.fill_form_input(dialog.find_element_by_css_selector('input[name="initialZoom"]'), '13')
            imgp = take_capture(self.driver, extra=25)
            crop_image(imgp, *create_box(dialog))

            dialog.find_element_by_css_selector(
                'button.btn-primary.styled_button').click()
            time.sleep(0.2)

            widg = get_by_contains(
                self.driver, '.fade.iwidget.in', 'Map Viewer')
            imgp = take_capture(self.driver, extra=26)
            crop_image(imgp, *create_box(widg))

            imgp = take_capture(self.driver, extra=27)
            crop_down(
                imgp, get_by_contains(self.driver, '.fade.iwidget.in', 'Linear Graph'))

            dialog = self.driver.find_element_by_css_selector(
                '.wirecloud_app_bar')
            btn = dialog.find_element_by_css_selector(
                '.wirecloud_toolbar .icon-puzzle-piece')
            ActionChains(self.driver).move_to_element(btn).perform()
            time.sleep(0.2)
            imgp = take_capture(self.driver, extra=28)
            add_pointer(imgp, get_position(btn, 0.8, 0.5))

            # End
            self.driver.find_element_by_css_selector(
                '.wirecloud_toolbar .icon-archive').click()
            time.sleep(0.2)
            self.driver.find_element_by_css_selector(
                '.wirecloud_header_nav .btn-large .icon-caret-left').click()

        with self.wiring_view as wiring:
            imgp = take_capture(self.driver, extra='Empty_Wiring_Operators')
            crop_down(
                imgp, self.driver.find_element_by_css_selector('.wiringEmptyBox'), 40)

            panel = self.driver.find_element_by_css_selector(
                '.se-container.se-bl-west-container.menubar')
            label_widg = get_by_text(panel, '.se-container.title', 'Widgets')
            # label_widg.click()
            operators_widg = get_by_text(
                panel, '.se-container.title', 'Operators')
            operators_widg.click()

            # Dragging the entity service
            ent_oper = get_by_text(
                panel, '.se-container.ioperator', 'NGSI source')
            # pos = get_position(ent_oper, 1.0, 1.0)
            ActionChains(self.driver).click_and_hold(
                ent_oper).move_by_offset(40, 20).perform()
            imgp = take_capture(self.driver, extra='Wiring_EntityService_drag')
            clon = get_by_text(
                self.driver, '.se-container.ioperator.clon', 'NGSI source')
            add_pointer(imgp, get_position(clon, 0.5, 0.6), False)
            crop_down(imgp, clon, 100)

            # Entity service added
            container = self.driver.find_element_by_css_selector(
                '.se-container.se-bl-center-container.grid')
            ActionChains(self.driver).move_by_offset(
                160, -180).release().perform()
            entservc = get_by_contains(
                container, '.se-container.ioperator', 'NGSI source')
            imgp = take_capture(self.driver, extra='Wiring_EntityService')
            add_pointer(imgp, get_position(entservc, 0.5, 0.5), False)
            crop_down(imgp, entservc, 250)

            conf_widg = get_by_contains(
                container, '.se-container.ioperator', 'NGSI source')

            # Add map iwidget
            label_widg.click()
            map_op = get_by_text(panel, '.se-container.iwidget', 'Map Viewer')
            move_elem(self.driver, map_op, 480, -90)
            # ActionChains(self.driver).click_and_hold(map_op).move_by_offset(450, -90).perform()
            # ActionChains(self.driver).release().perform()
            mapservc = get_by_contains(
                container, '.se-container.iwidget', 'Map Viewer')
            imgp = take_capture(
                self.driver, extra='Wiring_EntityService_MapViewer')
            add_pointer(imgp, get_position(mapservc, 0.5, 0.15), False)
            crop_down(imgp, mapservc, 10)

            labelprovideent = get_by_text(
                entservc, '.labelDiv', 'Provide entity')
            ActionChains(self.driver).move_to_element(
                labelprovideent).perform()
            time.sleep(0.6)  # wait for color transition
            imgp = take_capture(
                self.driver, extra='Wiring_EntityService_MapViewer_rec')
            add_image(
                imgp, get_position(labelprovideent, 0.7, 0.7), 'popup1.png')
            add_pointer(imgp, get_position(labelprovideent, 0.6, 0.5), False)
            crop_down(imgp, mapservc, 10)

            operators_widg.click()
            poi_oper = get_by_text(
                panel, '.se-container.ioperator', 'NGSI Entity To PoI')
            move_elem(self.driver, poi_oper, 200, 0)

            poiservc = get_by_contains(
                container, '.se-container.ioperator', 'NGSI Entity To PoI')

            # configure
            self.configure_ngsi_source(conf_widg)
            self.configure_ngsi_entity(poiservc)

            imgp = take_capture(self.driver, extra='Wiring_Entity2PoI')
            add_pointer(imgp, get_position(poiservc, 0.5, 0.45), False)
            crop_down(imgp, mapservc, 10)

            ActionChains(self.driver).move_to_element(
                labelprovideent).perform()
            time.sleep(0.6)  # wait for color transition
            imgp = take_capture(self.driver, extra='Wiring_Entity2PoI_rec')
            add_pointer(imgp, get_position(labelprovideent, 0.6, 0.5), False)
            crop_down(imgp, mapservc, 10)

            # PoI connection
            fromc = labelprovideent.find_element_by_css_selector(
                '.anchor.icon-circle')
            labelentity = get_by_text(poiservc, '.labelDiv', 'Entity')
            toc = labelentity.find_element_by_css_selector(
                '.anchor.icon-circle')

            ActionChains(self.driver).click_and_hold(
                fromc).move_by_offset(-100, 100).perform()
            time.sleep(0.2)
            imgp = take_capture(
                self.driver, extra='Wiring_Entity2PoI_connection')
            pos = get_position(fromc, 0.5, 0.5)
            pos = (pos[0] - 100, pos[1] + 100)
            add_pointer(imgp, pos, False)
            crop_down(imgp, mapservc, 10)

            ActionChains(self.driver).move_to_element(toc).release().perform()
            imgp = take_capture(self.driver, extra='Wiring_Entity2PoI_c_done')
            add_pointer(imgp, get_position(labelentity, 0.6, 0.5), False)
            crop_down(imgp, mapservc, 10)

            labelPoI = get_by_text(poiservc, '.labelDiv', 'PoI')
            fromc = labelPoI.find_element_by_css_selector(
                '.anchor.icon-circle')
            labelInsertUpdate = get_by_text(
                mapservc, '.labelDiv', 'Insert/Update PoI')
            toc = labelInsertUpdate.find_element_by_css_selector(
                '.anchor.icon-circle')
            ActionChains(self.driver).drag_and_drop(
                fromc, toc).move_to_element(labelInsertUpdate).perform()
            time.sleep(0.6)
            imgp = take_capture(self.driver, extra='Wiring_End_1st_ph')
            add_pointer(imgp, get_position(labelInsertUpdate, 0.6, 0.5), False)
            crop_down(imgp, mapservc, 10)

        # Out wiring
        imgp = take_capture(self.driver, extra='MapViewerWithEntities')

        with self.wiring_view as wiring:
            container = self.driver.find_element_by_css_selector(
                '.se-container.se-bl-center-container.grid')
            mapservc = get_by_contains(
                container, '.se-container.iwidget', 'Map Viewer')
            mapheader = mapservc.find_element_by_css_selector(
                '.se-container.se-bl-north-container.header')
            move_elem(self.driver, mapheader, 80, 100)
            svgpath = container.find_elements_by_css_selector('.null.arrow')[1]

            imgp = take_capture(self.driver, extra='delete_arrow1')
            add_pointer(imgp, get_position(svgpath, 0.5, 0.4), False)
            crop_down(imgp, mapservc, 10)

            svgbody = svgpath.find_element_by_css_selector('.arrowbody')
            svgbody.click()

            svgselect = container.find_element_by_css_selector(
                '.arrow.selected')
            center = svgselect.find_element_by_css_selector('.closer')
            imgp = take_capture(self.driver, extra='delete_arrow2')
            add_pointer(imgp, get_position(center, 0.5, 0.5), False)
            crop_down(imgp, mapservc, 10)

            upball, downball = svgselect.find_elements_by_css_selector(
                '.pullerBall')
            move_elem(self.driver, upball, 50, -50)
            # ActionChains(self.driver).click_and_hold(upball).move_by_offset(50, -50).release().perform()
            upball, downball = svgselect.find_elements_by_css_selector(
                '.pullerBall')
            imgp = take_capture(self.driver, extra='reshape_arrow1')
            add_pointer(imgp, get_position(upball, 0.3, 0.3), False)
            crop_down(imgp, mapservc, 10)

            move_elem(self.driver, downball, -50, 50)
            # ActionChains(self.driver).click_and_hold(downball).move_by_offset(-50, 50).release().perform()
            upball, downball = svgselect.find_elements_by_css_selector(
                '.pullerBall')
            imgp = take_capture(self.driver, extra='reshape_arrow2')
            add_pointer(imgp, get_position(downball, 0.3, 0.3), False)
            crop_down(imgp, mapservc, 10)

            container.find_element_by_css_selector('.canvas').click()

            entservc = get_by_contains(
                container, '.se-container.ioperator', 'NGSI source')
            setbutt = entservc.find_element_by_css_selector('.icon-cog')
            setbutt.click()
            popupmenu = self.driver.find_element_by_css_selector(
                '.se-popup-menu.se-popup-menu-bottom-left')
            minb = get_by_text(popupmenu, '.se-popup-menu-item', 'Minimize')
            ActionChains(self.driver).move_to_element(minb).perform()
            imgp = take_capture(self.driver, extra='minimize_option')
            add_pointer(imgp, get_position(minb, 0.7, 0.5), True)
            crop_down(imgp, mapservc, 10)
            minb.click()

            poiservc = get_by_contains(
                container, '.se-container.ioperator', 'NGSI Entity To PoI')
            setbutt = poiservc.find_element_by_css_selector('.icon-cog')
            setbutt.click()
            popupmenu = self.driver.find_element_by_css_selector(
                '.se-popup-menu.se-popup-menu-bottom-left')
            minb = get_by_text(popupmenu, '.se-popup-menu-item', 'Minimize')
            minb.click()
            time.sleep(0.4)
            imgp = take_capture(self.driver, extra=33)
            crop_down(imgp, mapservc, 10)

            # Configure all other elements
            # Move minimized
            mins_elems = container.find_elements_by_css_selector(
                '.se-container.reducedInt')
            map(lambda (e, x): move_elem(self.driver, e, x, 0),
                zip(mins_elems, [-100, -60]))
            move_elem(self.driver, mapheader, -260, 0)
            panel = self.driver.find_element_by_css_selector(
                '.se-container.se-bl-west-container.menubar')
            hm_oper = get_by_text(
                panel, '.se-container.ioperator', 'History Module to Linear Graph')
            move_elem(self.driver, hm_oper, 650, 80)
            label_widg = get_by_text(panel, '.se-container.title', 'Widgets')
            label_widg.click()
            lg_oper = get_by_text(
                panel, '.se-container.iwidget', 'Linear Graph')
            move_elem(self.driver, lg_oper, 650, 0)

            hm_wid = get_by_contains(
                container, '.se-container.ioperator', 'History Module to Linear Graph')
            lg_wid = get_by_contains(
                container, '.se-container.iwidget', 'Linear Graph')

            connect_anchors(
                self.driver, mapservc, hm_wid, 'PoI selected', 'Sensor Id')
            connect_anchors(
                self.driver, hm_wid, lg_wid, 'Historic Info', 'Data in')
            take_capture(self.driver, extra='FinalWiring')

            hm_wid.find_element_by_css_selector('.icon-cog').click()
            popup_menu = self.driver.find_element_by_css_selector(
                '.se-popup-menu.se-popup-menu-bottom-left')
            setts_btn = get_by_text(
                popup_menu, '.se-popup-menu-item', 'Settings')
            ActionChains(self.driver).move_to_element(setts_btn).perform()
            imgp = take_capture(self.driver, extra='HistoryOperatorSettings1')
            box = create_box(setts_btn, 40)
            box = (box[0], box[1], box[2] + 40, box[3] + 10)
            add_pointer(imgp, get_position(setts_btn, 0.7, 0.5), True)
            crop_image(imgp, *box)

            setts_btn.click()
            dialog = get_first_displayed(self.driver, '.window_menu')
            # self.fill_form_input(dialog.find_element_by_css_selector('input[name="number_of_days"]'), '15')
            imgp = take_capture(self.driver, extra='HistoryOperatorSettings2')
            crop_image(imgp, *create_box(dialog))
            dialog.find_element_by_css_selector(
                'button.btn-primary.styled_button').click()

        time.sleep(5.0)
        get_by_contains(self.driver, '.fade.iwidget.in', 'Map Viewer').find_element_by_css_selector(
            '.buttons .icon-cogs').click()
        get_by_contains(self.driver.find_element_by_css_selector(
            '.se-popup-menu.se-popup-menu-bottom-left'), '.se-popup-menu-item', 'Settings').click()
        dialog = get_first_displayed(self.driver, '.window_menu')
        self.fill_form_input(dialog.find_element_by_css_selector(
            'input[name="centerPreference"]'), 'Bajada de Polio, Santander')
        self.fill_form_input(
            dialog.find_element_by_css_selector('input[name="zoomPreference"]'), '15')
        dialog.find_element_by_css_selector('.btn-primary').click()
        time.sleep(1.0)
        imgp = take_capture(self.driver, extra=34)

        lg_path = image_path(extra=35)
        shutil.copy2(imgp, lg_path)
        crop_image(
            lg_path, *create_box(get_by_contains(self.driver, '.fade.iwidget.in', 'Linear Graph')))
        shutil.copy2(lg_path, image_path(extra='LinearGraphZoom1'))

        # Public workspace!
        popup_menu = self.open_menu()
        m_menu = popup_menu.get_entry('Settings')
        ActionChains(self.driver).move_to_element(m_menu).perform()
        imgp = take_capture(self.driver, extra='Public_Workspace_Menu')
        add_pointer(imgp, get_position(m_menu, 0.8, 0.5))
        crop_down(imgp, popup_menu.element, 80)
        m_menu.click()
        dialog = get_first_displayed(
            self.driver, '.window_menu.workspace_preferences')
        public_b = dialog.find_element_by_css_selector('input[name="public"]')
        public_b.click()
        imgp = take_capture(self.driver, extra='Public_Workspace_Settings')
        add_pointer(imgp, get_position(public_b, 0.5, 0.5))
        crop_image(imgp, *create_box(dialog))
        dialog.find_element_by_css_selector('.btn-primary').click()

        # Embed mashup!
        popup_menu = self.open_menu()
        m_menu = popup_menu.get_entry('Embed')
        ActionChains(self.driver).move_to_element(m_menu).perform()
        imgp = take_capture(self.driver, extra='Embed_Workspace_Menu')
        add_pointer(imgp, get_position(m_menu, 0.8, 0.5))
        crop_down(imgp, popup_menu.element, 80)
        m_menu.click()
        dialog = get_first_displayed(
            self.driver, '.window_menu.embed-code-window-menu')
        imgp = take_capture(self.driver, extra='Embed_Dialog')
        crop_image(imgp, *create_box(dialog))
        dialog.find_element_by_css_selector('.btn-primary').click()

    def clean_resources(self, resources):
        widgs = ['TestOperator', 'Test Mashup', 'Test']
        for w in widgs:
            resources.delete_resource(w)
        # "Test Mashup Dependencies" can't be removed

        get_by_text(self.driver, '.styled_button', 'Clear filters').click()

    test_building_mashup.tags = ('wirecloud-guide', 'ui-build-mashup')
