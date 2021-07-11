
$file = [System.IO.Path]::Join($pwd, "DCONFIG.xml")

$theme = New-Object xml
$theme.PreserveWhitespace = $true
$theme.Load($file)

$nodes = $theme.SelectNodes("//*[@roundness]")
foreach ($node in $nodes) {
    $node.roundness = "0.25"
}

$color_wire             = "#262626"
$color_object_selected  = "#f13a00"
$color_object_active    = "#ffcc40"
$color_vertex_select    = "#00ccff"
$color_edge_select      = "#00bbee"
$color_face             = "#ffffff1a"
$color_face_select      = "#00ccff20"
$color_edit_active      = "#fa00ffb9"


$theme.bpy.Theme.view_3d.ThemeView3D.wire               = $color_wire
$theme.bpy.Theme.view_3d.ThemeView3D.wire_edit          = $color_wire
$theme.bpy.Theme.view_3d.ThemeView3D.object_selected    = $color_object_selected
$theme.bpy.Theme.view_3d.ThemeView3D.object_active      = $color_object_active
$theme.bpy.Theme.view_3d.ThemeView3D.vertex_select      = $color_vertex_select
$theme.bpy.Theme.view_3d.ThemeView3D.edge_select        = $color_edge_select
$theme.bpy.Theme.view_3d.ThemeView3D.face               = $color_face
$theme.bpy.Theme.view_3d.ThemeView3D.face_select        = $color_face_select
$theme.bpy.Theme.view_3d.ThemeView3D.face_dot           = $color_vertex_select
$theme.bpy.Theme.view_3d.ThemeView3D.editmesh_active    = $color_edit_active


$theme.bpy.Theme.view_3d.ThemeView3D.extra_edge_len     = "#ffffff"
$theme.bpy.Theme.view_3d.ThemeView3D.extra_edge_angle   = "#ff00ff"
$theme.bpy.Theme.view_3d.ThemeView3D.extra_face_angle   = "#ffff00"
$theme.bpy.Theme.view_3d.ThemeView3D.extra_face_area    = "#00ff00"
$theme.bpy.Theme.view_3d.ThemeView3D.vertex_size        = "2"


$theme.bpy.Theme.image_editor.ThemeImageEditor.vertex_select    = $color_vertex_select
$theme.bpy.Theme.image_editor.ThemeImageEditor.edge_select      = $color_edge_select
$theme.bpy.Theme.image_editor.ThemeImageEditor.face             = $color_face
$theme.bpy.Theme.image_editor.ThemeImageEditor.face_select      = $color_face_select
$theme.bpy.Theme.image_editor.ThemeImageEditor.face_dot         = $color_vertex_select
$theme.bpy.Theme.image_editor.ThemeImageEditor.editmesh_active  = $color_edit_active


$theme.bpy.Theme.node_editor.ThemeNodeEditor.group_node     = "#426628d9"
$theme.bpy.Theme.node_editor.ThemeNodeEditor.noodle_curving = "3"


$theme.bpy.Theme.outliner.ThemeOutliner.selected_object = $color_object_selected
$theme.bpy.Theme.outliner.ThemeOutliner.active_object   = $color_object_active


$settings = New-Object System.Xml.XmlWriterSettings
$settings.OmitXmlDeclaration = $true
$settings.NewLineOnAttributes = $true
$settings.Indent = $true
$settings.NewLineChars ="`r`n"
$settings.Encoding = New-Object System.Text.UTF8Encoding( $false )
$w = [System.Xml.XmlWriter]::Create($file, $settings)
$theme.Save($w)
$w.Close()
