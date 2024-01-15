# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import open3d as o3d
import numpy as np
import logging
import tkinter.filedialog


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
DEBUG_FOLDER="LOCALIZATION_DEBUG"

class ItemViewer:
    geometries = []
    scene_pcd = []
    idx = 0
    draw_bbox = True
    item_visible = True
    draw_edges = False

    def __init__(self, scene_pcd, boundary_pcd = None):
        self.scene_pcd = scene_pcd
        self.boundary_pcd = boundary_pcd
        

    def load_geometries(self, path: str):
        log.info(f"Loading pointclouds from {path}")

        self.geometries = []
        self.idx = 0

        for file in os.listdir(path):
            if file.endswith(".ply"):
                filepath = os.path.join(path, file)
                item = {"pcd": o3d.io.read_point_cloud(filepath)}

                item["pcd"].paint_uniform_color(np.array([1, 0, 0]))
                item["id"] = file.split(".")[0]
                with open(os.path.join(path, file.split(".")[0] + ".dbg"), "r") as f:
                    item["text"] = f.read()
                item["bbox"] = item["pcd"].get_minimal_oriented_bounding_box()

                self.geometries.append(item)
        log.info(f"Loaded {len(self.geometries)} pointclouds")

    def load_geometries_cbk(self, vis):
        path = tkinter.filedialog.askdirectory(title="Select rejected folder", 
                                        initialdir=DEBUG_FOLDER)

        try:
            self.remove_current_item(vis)
        except Exception as e:
            log.error(f"Could not remove current item: {e}")
        if path:
            self.load_geometries(path)
        else:
            log.warning("No path selected")
        return False
    
    def statistics_cbk(self, vis):
        parameters = {}
        log.info("Computing statistics...")
        for item in self.geometries:
            if text := item.get("text", ""):
                params = text.split("\n")
                for param_line in params:
                    if ":" in param_line:
                        try:
                            key, value = param_line.split(":")
                            if key not in parameters:
                                parameters[key] = []
                            parameters[key].append(float(value))
                            log.debug(f"item {item['id']}::{key}={value}")
                        except Exception as e:
                            log.error(f"Could not parse line {param_line}: {e}")

        for key, values in parameters.items():
            try:
                log.info(f"{key}: mean={np.mean(values)}")
                log.info(f"{key}: std={np.std(values)}")
                log.info(f"{key}: min={np.min(values)}")
                log.info(f"{key}: max={np.max(values)}")
            except Exception as e:
                log.error(f"Could not compute statistics for {key}: {e}")

    def toggle_background(self, vis):
        opt = vis.get_render_option()
        bg_color = opt.background_color
        new_color = np.array([0, 0, 0]) if bg_color.all() else np.array([1, 1, 1])
        opt.background_color = new_color
        return False
    
    def toggle_item_visibility(self, vis):
        if self.item_visible:
            self.remove_current_item(vis)
        else:
            self.add_current_item(vis)
        return False

    def next_item(self, vis):
        self.remove_current_item(vis)
        self.idx = (self.idx + 1) % len(self.geometries)
        self.add_current_item(vis)
        log.info(f'{self.idx}::{self.geometries[self.idx]["id"]}: \n{self.geometries[self.idx]["text"]}')
        return False

    def previous_item(self, vis):
        self.remove_current_item(vis)
        self.idx = (self.idx - 1) % len(self.geometries)
        self.add_current_item(vis)
        log.info(f'{self.idx}::{self.geometries[self.idx]["id"]}: \n{self.geometries[self.idx]["text"]}')
        return False
    
    def add_current_item(self, vis):
        if not self.item_visible:
            vis.add_geometry(self.geometries[self.idx]["pcd"], reset_bounding_box=False)
            if self.draw_bbox:
                vis.add_geometry(self.geometries[self.idx]["bbox"], reset_bounding_box=False)
            self.item_visible = True

    def remove_current_item(self, vis):
        if self.item_visible:
            vis.remove_geometry(self.geometries[self.idx]["pcd"], reset_bounding_box=False)
            vis.remove_geometry(self.geometries[self.idx]["bbox"], reset_bounding_box=False)
            self.item_visible=False

    def update_item(self, vis):
        self.remove_current_item(vis)
        self.add_current_item(vis)

    def toggle_bbox(self, vis):
        self.draw_bbox = not self.draw_bbox
        self.update_item(vis)

    def toggle_edges(self, vis):
        if self.draw_edges:
            self._remove_edges(vis)
        else:
            self._add_edges(vis)

    def _add_edges(self, vis):
        if self.boundary_pcd and not self.draw_edges:
            vis.add_geometry(self.boundary_pcd, reset_bounding_box=False)
            self.draw_edges = True

    def _remove_edges(self, vis):
        if self.boundary_pcd and self.draw_edges:
            vis.remove_geometry(self.boundary_pcd, reset_bounding_box=False)
            self.draw_edges = False

    def reset_view_cbk(self, vis):
        # make the camera look at the center of the scene
        ctr = vis.get_view_control()
        ctr.set_front([0, 0, -1])
        ctr.set_lookat(self.scene_pcd.get_center())
        
        vis.update_renderer()

    def run(self):
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window()

        vis.add_geometry(self.scene_pcd)
        log.info(f"Center of scene: {self.scene_pcd.get_center()}")


        vis.add_geometry(self.geometries[self.idx]["pcd"])
        vis.add_geometry(self.geometries[self.idx]["bbox"])

        log.info(f'{self.idx}::{self.geometries[self.idx]["id"]}: \n{self.geometries[self.idx]["text"]}')

        origin_mesh = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=100, origin=[0, 0, 0])
        vis.add_geometry(origin_mesh)
        vis.register_key_callback(ord("C"), self.toggle_background)
        vis.register_key_callback(ord("J"), self.previous_item)
        vis.register_key_callback(ord("L"), self.next_item)
        vis.register_key_callback(ord("B"), self.toggle_bbox)
        vis.register_key_callback(ord("O"), self.load_geometries_cbk)
        vis.register_key_callback(ord("K"), self.toggle_item_visibility)
        vis.register_key_callback(ord("E"), self.toggle_edges)
        vis.register_key_callback(ord("R"), self.reset_view_cbk)
        vis.register_key_callback(ord("S"), self.statistics_cbk)

        self.reset_view_cbk(vis)        

        # try to load view from json:
        try:
            vis.get_render_option().load_from_json("viewpoint.json")
        except Exception as e:
            log.warning(f"Could not load viewpoint: {e}")

        vis.run()
        vis.destroy_window()
        
        
if __name__ == "__main__":
    
    help = """
    [+/-] Increase/decrease point size
    [R] Reset view
    [C] Toggle background color (black/white)
    [J] Previous item
    [K] Toggle item visibility (on/off)
    [L] Next item
    [B] Toggle bounding box outline (on/off)
    [O] Load new items (folder)
    [N] Toggle normal rendering (on/off)
    [E] Toggle edges (on/off)
    [Q] Quit
    """
    print(help)

    sdk_folder = os.path.join(os.environ["APPDATA"], "PhotoneoLocalizationSDK")
    os.chdir(sdk_folder)
    if DEBUG_FOLDER not in os.listdir():
        # navigate to AppData folder
        log.error(f"Could not find debug date in folder {sdk_folder}")
        raise FileNotFoundError("Could not find debug folder")
    
    # load scene point cloud
    scene_pcd = o3d.io.read_point_cloud(os.path.join(DEBUG_FOLDER, "scene_surface.ply"))
    boundary_pcd = o3d.io.read_point_cloud(os.path.join(DEBUG_FOLDER, "scene_boundary.ply"))
    # log.info scene info
    log.info("Scene point cloud:")
    log.info(scene_pcd)
    log.info("Boundary point cloud:")
    log.info(boundary_pcd)
    
    # paint point cloud grey
    grey_color = np.array([0.4, 0.4, 0.4])
    scene_pcd.paint_uniform_color(grey_color)
    ligh_blue_color = np.array([0.3, 0.3, .8])
    boundary_pcd.paint_uniform_color(ligh_blue_color)


    viewer = ItemViewer(scene_pcd, boundary_pcd)
    viewer.load_geometries(
        tkinter.filedialog.askdirectory(title="Select rejected folder", 
                                        initialdir=DEBUG_FOLDER)
                                        )
    viewer.run()