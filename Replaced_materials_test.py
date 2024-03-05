import omni.ext
import omni.ui as ui
import omni.kit.notification_manager as nm

import omni.usd
from pxr import Usd, Sdf

import omni.kit.commands
from pxr import Sdf

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[replaced_materials_with_that_material_test] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Replaced_materials_with_that_material_testExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self) -> None:
        super().__init__()
        self.viewport_scene = None
        self.widget_view_on = False
        self.ext_id = None

    def on_startup(self, ext_id):
        self.window = ui.Window("Replaced Materials Test", width=300, height=150)
        self.ext_id = ext_id

        with self.window.frame:
            with ui.VStack():
                with ui.HStack(height=10):
                    ui.Label("Prim Name", width=120)
                    ui.Spacer(width=20)
                    self.prim_name_model = ui.SimpleStringModel()
                    ui.StringField(model=self.prim_name_model)
                    ui.Button("Select", clicked_fn=self.select_prims_by_name)

                with ui.HStack(height=10):
                    # 공백, 한줄띄기
                    ui.Spacer()

                with ui.HStack(height=10):
                    ui.Label("Material Name", width=120)
                    ui.Spacer(width=20)
                    self.material_name_model = ui.SimpleStringModel()
                    ui.StringField(model=self.material_name_model)
                    ui.Button("Apply", clicked_fn=self.replace_material)

                with ui.HStack(height=10):
                    # 공백, 한줄띄기
                    ui.Spacer()

                with ui.HStack():
                    # 드롭다운
                    with ui.CollapsableFrame("Prim Info", height=80):
                        with ui.VStack():
                            with ui.HStack(height=10):
                                self.select = ui.Label("None Selected", width=120, alignment=ui.Alignment.CENTER)
                        
                            with ui.HStack(height=5):
                                ui.Spacer()

                            with ui.HStack(height=10):
                                ui.Button("Copy", clicked_fn=self.copy_selected)
                                ui.Button("Delete", clicked_fn=self.delete_selected)

    def copy_selected(self):
        if self.select.text != "None Selected":
            omni.kit.commands.execute('CopyPrim', path_from=self.select.text)
            self.select.text = "None Selected"
        else:
            nm.post_notification(
                "None Selected",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
        return
    
    def delete_selected(self):
        if self.select.text != "None Selected":
            omni.kit.commands.execute('DeletePrims', paths=[self.select.text])
            self.select.text = "None Selected"
        else:
            nm.post_notification(
                "None Selected",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
        return

    def select_prims_by_name(self):
        stage = omni.usd.get_context().get_stage()
        # Prime_name 입력받기 ex) Cube
        prim_name = self.prim_name_model.get_value_as_string()
        if prim_name == "":
            nm.post_notification(
                "Enter the prim want to find",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
            return

        if not stage:
            nm.post_notification(
                "No any Stage",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
            return
        # 경로정보 가져오기
        found_prims = [x for x in stage.Traverse() if x.GetName() == prim_name]
        # found_prims = [x for x in stage.Traverse() if prim_name in x.GetName()]
        if not found_prims:
            nm.post_notification(
                "No " + prim_name + " prims in stage",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
            return
        
        startIdx = str(found_prims[0]).find('<')
        endIdx = str(found_prims[0]).find('>')
        prims = str(found_prims)
        self.select.text = prims[startIdx + 2: endIdx + 1]
        # 경로만 가져오기
        prims = prims[startIdx + 2: endIdx + 1]
        
        ctx = omni.usd.get_context()

        # omni.kit.commands.execute('SelectPrimsCommand',
        #     old_selected_paths=[],
        #     new_selected_paths=['/World/Cone_02', '/World/Cone_01', '/World/Cone'],
        #     expand_in_stage=True)

        selected = ctx.get_selection().get_selected_prim_paths()

        # 하나 선택되면 작업
        if prims in selected and len(selected) == 1:
            nm.post_notification(
                "Already Selected",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )
            return

        result = ctx.get_selection().set_selected_prim_paths([prims], True)
        
        if result == False:
            nm.post_notification(
                "No any prims",
                hide_after_timeout=True,
                duration=1,
                status=nm.NotificationStatus.WARNING,
            )

        return

    def replace_material(self):
        prim_name = self.prim_name_model.get_value_as_string()
        material_name = self.material_name_model.get_value_as_string()
        omni.kit.commands.execute('BindMaterialCommand',
            prim_path='/World/'+prim_name,
            # prim_path='/World/Cube*',
            material_path='/World/Looks/'+material_name)
            # https://docs.omniverse.nvidia.com/extensions/latest/ext_omnigraph/node-library/nodes/omni-graph-nodes/readprims-3.html 참고

        # stage = omni.usd.get_context().get_stage()
        # if material_name in stage.Traverse():
        #     omni.kit.commands.execute('BindMaterialCommand',
        #         prim_path='/World/'+prim_name,
        #         # prim_path='/World/Cube*',
        #         material_path='/World/Looks/'+material_name)
        #         # https://docs.omniverse.nvidia.com/extensions/latest/ext_omnigraph/node-library/nodes/omni-graph-nodes/readprims-3.html 참고
        # else:
        #     nm.post_notification(
        #     "No " + material_name + " prims in stage",
        #     hide_after_timeout=True,
        #     duration=1,
        #     status=nm.NotificationStatus.WARNING,
        #     )
        #     return


