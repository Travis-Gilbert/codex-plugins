# Tauri 2 Native Feature Implementation

## Menu API

### Menu Bar (macOS / Windows / Linux)

```rust
use tauri::menu::{Menu, MenuItem, Submenu, PredefinedMenuItem, CheckMenuItem};

fn build_menu(handle: &tauri::AppHandle) -> tauri::Result<Menu<tauri::Wry>> {
    Menu::with_items(handle, &[
        // macOS app menu (ignored on Windows/Linux)
        &Submenu::with_items(handle, "App Name", true, &[
            &PredefinedMenuItem::about(handle, Some("About App Name"), None)?,
            &PredefinedMenuItem::separator(handle)?,
            &MenuItem::with_id(handle, "preferences", "Preferences...", true, Some("CmdOrCtrl+,"))?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::services(handle, None)?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::hide(handle, None)?,
            &PredefinedMenuItem::hide_others(handle, None)?,
            &PredefinedMenuItem::show_all(handle, None)?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::quit(handle, None)?,
        ])?,

        &Submenu::with_items(handle, "File", true, &[
            &MenuItem::with_id(handle, "new", "New Object", true, Some("CmdOrCtrl+N"))?,
            &MenuItem::with_id(handle, "capture", "Quick Capture", true, Some("CmdOrCtrl+Shift+Space"))?,
            &PredefinedMenuItem::separator(handle)?,
            &MenuItem::with_id(handle, "import", "Import...", true, Some("CmdOrCtrl+I"))?,
            &MenuItem::with_id(handle, "export", "Export...", true, Some("CmdOrCtrl+E"))?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::close_window(handle, None)?,
        ])?,

        &Submenu::with_items(handle, "Edit", true, &[
            &PredefinedMenuItem::undo(handle, None)?,
            &PredefinedMenuItem::redo(handle, None)?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::cut(handle, None)?,
            &PredefinedMenuItem::copy(handle, None)?,
            &PredefinedMenuItem::paste(handle, None)?,
            &PredefinedMenuItem::select_all(handle, None)?,
        ])?,

        &Submenu::with_items(handle, "View", true, &[
            &MenuItem::with_id(handle, "sidebar", "Toggle Sidebar", true, Some("CmdOrCtrl+/"))?,
            &MenuItem::with_id(handle, "inspector", "Toggle Inspector", true, Some("CmdOrCtrl+\\"))?,
            &MenuItem::with_id(handle, "palette", "Command Palette", true, Some("CmdOrCtrl+K"))?,
            &PredefinedMenuItem::separator(handle)?,
            &CheckMenuItem::with_id(handle, "dark_mode", "Dark Mode", true, true, None::<&str>)?,
            &PredefinedMenuItem::separator(handle)?,
            &PredefinedMenuItem::fullscreen(handle, None)?,
        ])?,

        &Submenu::with_items(handle, "Window", true, &[
            &PredefinedMenuItem::minimize(handle, None)?,
            &PredefinedMenuItem::maximize(handle, None)?,
        ])?,
    ])
}
```

### Menu Event Handling

```rust
.on_menu_event(|app, event| {
    let window = app.get_webview_window("main").unwrap();
    match event.id().as_ref() {
        "new" => { window.emit("menu:new", ()).unwrap(); }
        "capture" => { window.emit("menu:capture", ()).unwrap(); }
        "sidebar" => { window.emit("menu:toggle-sidebar", ()).unwrap(); }
        "inspector" => { window.emit("menu:toggle-inspector", ()).unwrap(); }
        "palette" => { window.emit("menu:open-palette", ()).unwrap(); }
        "preferences" => { window.emit("menu:preferences", ()).unwrap(); }
        _ => {}
    }
})
```

### Frontend Event Listener

```typescript
import { listen } from '@tauri-apps/api/event';

useEffect(() => {
  const unlisten = listen('menu:toggle-sidebar', () => {
    toggleSidebar();
  });
  return () => { unlisten.then(fn => fn()); };
}, []);
```

## System Tray (TrayIcon)

```rust
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton};
use tauri::menu::{Menu, MenuItem};

fn setup_tray(app: &tauri::App) -> tauri::Result<()> {
    let menu = Menu::with_items(app.handle(), &[
        &MenuItem::with_id(app.handle(), "show", "Show Window", true, None::<&str>)?,
        &MenuItem::with_id(app.handle(), "capture", "Quick Capture", true, None::<&str>)?,
        &MenuItem::with_id(app.handle(), "quit", "Quit", true, None::<&str>)?,
    ])?;

    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .tooltip("App Name - Running")
        .menu(&menu)
        .on_menu_event(|app, event| {
            match event.id().as_ref() {
                "show" => {
                    let window = app.get_webview_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "capture" => { app.emit("tray:capture", ()).unwrap(); }
                "quit" => { app.exit(0); }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click { button: MouseButton::Left, .. } = event {
                let window = tray.app_handle().get_webview_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
        })
        .build(app)?;

    Ok(())
}
```

## Notification Plugin

```toml
# Cargo.toml
[dependencies]
tauri-plugin-notification = "2"
```

```rust
// Rust side
use tauri_plugin_notification::NotificationExt;

app.notification()
    .builder()
    .title("New Connection")
    .body("3 new connections discovered")
    .show()
    .unwrap();
```

```typescript
// JavaScript side
import { sendNotification, isPermissionGranted, requestPermission } from '@tauri-apps/plugin-notification';

async function notify(title: string, body: string) {
  let granted = await isPermissionGranted();
  if (!granted) {
    const permission = await requestPermission();
    granted = permission === 'granted';
  }
  if (granted) {
    sendNotification({ title, body });
  }
}
```

## Updater Plugin

```toml
# Cargo.toml
[dependencies]
tauri-plugin-updater = "2"
```

```typescript
// JavaScript: check for updates
import { check } from '@tauri-apps/plugin-updater';

async function checkForUpdates() {
  const update = await check();
  if (update) {
    const confirmed = confirm(`Update ${update.version} available. Install now?`);
    if (confirmed) {
      await update.downloadAndInstall();
      // Restart the app
      const { relaunch } = await import('@tauri-apps/plugin-process');
      await relaunch();
    }
  }
}
```

## File System Plugin

```typescript
import { readTextFile, writeTextFile, exists } from '@tauri-apps/plugin-fs';
import { appDataDir, join } from '@tauri-apps/api/path';

async function saveUserData(filename: string, data: string) {
  const dir = await appDataDir();
  const path = await join(dir, filename);
  await writeTextFile(path, data);
}

async function loadUserData(filename: string): Promise<string | null> {
  const dir = await appDataDir();
  const path = await join(dir, filename);
  if (await exists(path)) {
    return readTextFile(path);
  }
  return null;
}
```

## Global Shortcut Plugin

```rust
use tauri_plugin_global_shortcut::GlobalShortcutExt;

app.global_shortcut().register("CmdOrCtrl+Shift+Space", |app, _shortcut, _event| {
    // Show/create capture window
    if let Some(window) = app.get_webview_window("capture") {
        window.show().unwrap();
        window.set_focus().unwrap();
    }
})?;
```

## Deep Link Plugin

```rust
// Register custom URL protocol: myapp://
use tauri_plugin_deep_link::DeepLinkExt;

app.deep_link().register("myapp")?;

app.deep_link().on_open_url(|event| {
    let urls = event.urls();
    for url in urls {
        // Parse URL and route to correct view
        // e.g., myapp://objects/abc123
        app.emit("deep-link", url.to_string()).unwrap();
    }
});
```

## Window State Plugin

Remembers window position and size across launches:

```toml
# Cargo.toml
[dependencies]
tauri-plugin-window-state = "2"
```

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_window_state::Builder::new().build())
```

No additional configuration needed — the plugin automatically saves and restores window state.

## Autostart Plugin

Launch on login:

```rust
use tauri_plugin_autostart::MacosLauncher;

tauri::Builder::default()
    .plugin(tauri_plugin_autostart::init(
        MacosLauncher::LaunchAgent,
        Some(vec!["--minimized"]),
    ))
```
