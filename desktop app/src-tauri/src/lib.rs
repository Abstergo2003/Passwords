#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use window_vibrancy::*;
use tauri::webview::WebviewWindowBuilder;

#[tauri::command]
async fn open_attach(handle: tauri::AppHandle) {
    let folder_window = WebviewWindowBuilder::new(
        &handle,
        "external", // unique label
        tauri::WebviewUrl::App("index.html#/attachment".into())
    )
    .decorations(false)
    .transparent(true)
    .inner_size(1000.0, 1000.0)
    .build()
    .unwrap();

    #[cfg(target_os = "windows")]
    apply_acrylic(folder_window.clone(), Some((0, 0, 0, 0)))
        .expect("Unsupported platform! 'apply_acrylic' is only supported on Windows");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![open_attach])
        .setup(|app| {
            let main_window = WebviewWindowBuilder::new(
                app,
                "local",
                tauri::WebviewUrl::App("index.html".into())
            )
            .decorations(false)
            .transparent(true)
            .inner_size(1000.0, 700.0)
            .build()?;

            main_window.set_resizable(false).unwrap();

            #[cfg(target_os = "windows")]
            apply_acrylic(main_window, Some((0, 0, 0, 0)))
                .expect("Unsupported platform! 'apply_acrylic' is only supported on Windows");

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
