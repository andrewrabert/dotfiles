use clap::Parser;
use std::fs;
use std::process::Command;
use zbus::blocking::Connection;
use zbus::zvariant::Value;

#[derive(Parser, Debug)]
#[command(
    about = "Utility to launch a window (or raise it, if it was minimized), or to show information about the active window, or to perform other operations with windows in KDE Plasma. It interacts with KWin using KWin scripts and it is compatible with X11 and Wayland.",
    arg_required_else_help = true
)]
struct Args {
    /// Show information about the active window
    #[arg(short = 'i', long = "info-active")]
    info_active: bool,

    /// Filter by window class (exact match)
    #[arg(short = 'f', long = "filter")]
    filter: Option<String>,

    /// Filter by window title (caption)
    #[arg(short = 'a', long = "filter-alternative")]
    filter_alt: Option<String>,

    /// Filter by window class using regex pattern
    #[arg(short = 'r', long = "filter-regex")]
    filter_regex: Option<String>,

    /// Operate on the currently focused window
    #[arg(short = 'F', long = "filter-focused")]
    filter_focused: bool,

    /// Also minimize the window if it is already active
    #[arg(short = 't', long = "toggle")]
    toggle: bool,

    /// Center the window on screen (optional: "always" or "initial")
    #[arg(short = 'c', long = "center", num_args = 0..=1, default_missing_value = "always")]
    center: Option<String>,

    /// Scale factor for center-scale
    #[arg(long = "scale-factor")]
    scale_factor: Option<f64>,

    /// Maximum aspect ratio for center-scale
    #[arg(long = "max-aspect")]
    max_aspect: Option<f64>,

    /// Window width (pixels or percentage, e.g. "800" or "80%")
    #[arg(long = "width")]
    width: Option<String>,

    /// Window height (pixels or percentage, e.g. "600" or "80%")
    #[arg(long = "height")]
    height: Option<String>,

    /// Minimum window width (pixels or percentage)
    #[arg(long = "min-width")]
    min_width: Option<String>,

    /// Maximum window width (pixels or percentage)
    #[arg(long = "max-width")]
    max_width: Option<String>,

    /// Minimum window height (pixels or percentage)
    #[arg(long = "min-height")]
    min_height: Option<String>,

    /// Maximum window height (pixels or percentage)
    #[arg(long = "max-height")]
    max_height: Option<String>,

    /// Command to run if no process is found
    #[arg(trailing_var_arg = true)]
    command: Vec<String>,

    /// Override the process name used when checking if running
    #[arg(short = 'p', long = "process")]
    process: Option<String>,

    /// Only search processes of the current user (requires loginctl)
    #[arg(short = 'u', long = "current-user")]
    current_user: bool,
}

fn build_script(
    filter: &str,
    filter_alt: &str,
    filter_regex: &str,
    toggle: bool,
    center: Option<&str>,
    scale_factor: Option<f64>,
    max_aspect: Option<f64>,
    width: Option<&str>,
    height: Option<&str>,
    min_width: Option<&str>,
    max_width: Option<&str>,
    min_height: Option<&str>,
    max_height: Option<&str>,
    filter_focused: bool,
) -> String {
    let mut script = String::new();

    let needs_resize = width.is_some() || height.is_some() || scale_factor.is_some()
        || min_width.is_some() || max_width.is_some() || min_height.is_some() || max_height.is_some();
    let do_center = center.is_some();

    // parseSize only if needed
    if needs_resize {
        script.push_str(r#"function parseSize(v,s){if(v===null||v==='')return null;var t=String(v);if(t.endsWith('%'))return s*(parseFloat(t.slice(0,-1))/100);return parseFloat(t);}
"#);
    }

    // setActiveClient - build only what's needed
    script.push_str("function setActiveClient(c){c.minimized=false;");

    if needs_resize || do_center {
        script.push_str("var scr=workspace.activeScreen,sw=scr.geometry.width,sh=scr.geometry.height,w=c.frameGeometry.width,h=c.frameGeometry.height;");

        if let Some(sf) = scale_factor {
            script.push_str(&format!("var wsW=sw,wsH=sh;"));
            if let Some(ma) = max_aspect {
                script.push_str(&format!("if((wsW/wsH)>{}){{wsH=Math.min(wsW,wsH);wsW=wsH*{};}}", ma, ma));
            }
            script.push_str(&format!("w=wsW*{};h=wsH*{};", sf, sf));
        } else if width.is_some() || height.is_some() {
            if let Some(w_val) = width {
                script.push_str(&format!("w=parseSize('{}',sw)||w;", w_val));
            }
            if let Some(h_val) = height {
                script.push_str(&format!("h=parseSize('{}',sh)||h;", h_val));
            }
        }

        // min/max constraints
        if let Some(v) = min_width {
            script.push_str(&format!("var minW=parseSize('{}',sw);if(minW)w=Math.max(minW,w);", v));
        }
        if let Some(v) = max_width {
            script.push_str(&format!("var maxW=parseSize('{}',sw);if(maxW)w=Math.min(maxW,w);", v));
        }
        if let Some(v) = min_height {
            script.push_str(&format!("var minH=parseSize('{}',sh);if(minH)h=Math.max(minH,h);", v));
        }
        if let Some(v) = max_height {
            script.push_str(&format!("var maxH=parseSize('{}',sh);if(maxH)h=Math.min(maxH,h);", v));
        }

        if do_center {
            script.push_str("var x=(sw-w)/2,y=(sh-h)/2;");
        } else {
            script.push_str("var x=c.frameGeometry.x,y=c.frameGeometry.y;");
        }

        script.push_str("c.frameGeometry={x:x,y:y,width:w,height:h};");
    }

    script.push_str("if(workspace.activeClient!==undefined)workspace.activeClient=c;else workspace.activeWindow=c;}");

    // Main logic
    if filter_focused {
        script.push_str("var aw=workspace.activeClient||workspace.activeWindow;if(aw)setActiveClient(aw);");
    } else {
        script.push_str("var aw=workspace.activeClient||workspace.activeWindow;");
        script.push_str("var cs=workspace.clientList?workspace.clientList():workspace.windowList();var m=[];");

        // Build matching logic based on what filters are provided
        if !filter.is_empty() {
            script.push_str(&format!("for(var i=0;i<cs.length;i++)if(cs[i].resourceClass=='{}')m.push(cs[i]);", filter));
        } else if !filter_regex.is_empty() {
            script.push_str(&format!("var re=new RegExp('{}');for(var i=0;i<cs.length;i++)if(re.exec(cs[i].resourceClass))m.push(cs[i]);", filter_regex));
        } else if !filter_alt.is_empty() {
            script.push_str(&format!("var re=new RegExp('{}','i');for(var i=0;i<cs.length;i++)if(re.exec(cs[i].caption))m.push(cs[i]);", filter_alt));
        }

        script.push_str("if(m.length===1){var c=m[0];if(aw!==c)setActiveClient(c);");
        if toggle {
            script.push_str("else c.minimized=!c.minimized;");
        }
        script.push_str("}else if(m.length>1){m.sort(function(a,b){return a.stackingOrder-b.stackingOrder;});setActiveClient(m[0]);}");
    }

    script
}

fn get_connection() -> Result<Connection, String> {
    Connection::session().map_err(|e| e.to_string())
}

fn kwin_support_information(conn: &Connection) -> Result<String, String> {
    conn.call_method(
        Some("org.kde.KWin"),
        "/KWin",
        Some("org.kde.KWin"),
        "supportInformation",
        &(),
    )
    .map_err(|e| e.to_string())?
    .body()
    .deserialize::<String>()
    .map_err(|e| e.to_string())
}

fn kwin_get_window_info(conn: &Connection, window_id: &str) -> Result<String, String> {
    let reply = conn
        .call_method(
            Some("org.kde.KWin"),
            "/KWin",
            Some("org.kde.KWin"),
            "getWindowInfo",
            &window_id,
        )
        .map_err(|e| e.to_string())?;

    // getWindowInfo returns a vardict, format it nicely
    let body = reply.body();
    let value: Value = body.deserialize().map_err(|e| e.to_string())?;
    Ok(format!("{:#?}", value))
}

fn kwin_load_script(conn: &Connection, path: &str, name: &str) -> Result<i32, String> {
    conn.call_method(
        Some("org.kde.KWin"),
        "/Scripting",
        Some("org.kde.kwin.Scripting"),
        "loadScript",
        &(path, name),
    )
    .map_err(|e| e.to_string())?
    .body()
    .deserialize::<i32>()
    .map_err(|e| e.to_string())
}

fn kwin_load_script_no_name(conn: &Connection, path: &str) -> Result<i32, String> {
    conn.call_method(
        Some("org.kde.KWin"),
        "/Scripting",
        Some("org.kde.kwin.Scripting"),
        "loadScript",
        &(path,),
    )
    .map_err(|e| e.to_string())?
    .body()
    .deserialize::<i32>()
    .map_err(|e| e.to_string())
}

fn kwin_script_run(conn: &Connection, path: &str, interface: &str) -> Result<(), String> {
    conn.call_method(
        Some("org.kde.KWin"),
        path,
        Some(interface),
        "run",
        &(),
    )
    .map_err(|e| e.to_string())?;
    Ok(())
}

fn kwin_script_stop(conn: &Connection, path: &str, interface: &str) -> Result<(), String> {
    conn.call_method(
        Some("org.kde.KWin"),
        path,
        Some(interface),
        "stop",
        &(),
    )
    .map_err(|e| e.to_string())?;
    Ok(())
}

fn get_kwin_version(conn: &Connection) -> Result<String, String> {
    let support_info = kwin_support_information(conn)?;
    for line in support_info.lines() {
        if line.contains("KWin version:") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 3 {
                return Ok(parts[2].to_string());
            }
        }
    }
    Err("Could not determine KWin version".to_string())
}

fn parse_version(v: &str) -> Vec<u32> {
    v.split('.')
        .filter_map(|s| s.parse().ok())
        .collect()
}

fn ver_cmp(a: &str, b: &str) -> std::cmp::Ordering {
    let va = parse_version(a);
    let vb = parse_version(b);
    va.cmp(&vb)
}

fn ver_between(min: &str, actual: &str, max: &str) -> bool {
    ver_cmp(min, actual) != std::cmp::Ordering::Greater
        && ver_cmp(actual, max) != std::cmp::Ordering::Greater
}

fn ver_lt(a: &str, b: &str) -> bool {
    ver_cmp(a, b) == std::cmp::Ordering::Less
}

fn info_active(conn: &Connection) -> Result<(), String> {
    let kwin_version = get_kwin_version(conn)?;
    let major: u32 = kwin_version
        .split('.')
        .next()
        .and_then(|s| s.parse().ok())
        .ok_or("Invalid version")?;

    if major < 6 {
        eprintln!("ERROR: This feature needs KWin 6 or later.");
        std::process::exit(1);
    }

    let js_file = tempfile::NamedTempFile::new()
        .map_err(|e| e.to_string())?;
    let js_path = js_file.path().to_str().ok_or("Invalid temp path")?.to_string();

    let output_file = tempfile::NamedTempFile::new()
        .map_err(|e| e.to_string())?;
    let output_path = output_file.path().to_str().ok_or("Invalid temp path")?.to_string();

    // KWin script that writes window ID to a file
    let script_content = format!(
        r#"
        var file = new QFile("{}");
        file.open(QIODevice.WriteOnly);
        var stream = new QTextStream(file);
        stream.writeString(String(workspace.activeWindow.internalId));
        file.close();
        "#,
        output_path
    );

    fs::write(&js_file, script_content).map_err(|e| e.to_string())?;

    let script_id = kwin_load_script_no_name(conn, &js_path)?;

    let script_path = format!("/Scripting/Script{}", script_id);
    kwin_script_run(conn, &script_path, "org.kde.kwin.Script")?;

    // Small delay to let script execute
    std::thread::sleep(std::time::Duration::from_millis(50));

    let window_id = fs::read_to_string(&output_path)
        .map_err(|e| format!("Could not read output file: {}", e))?;
    let window_id = window_id.trim();

    kwin_script_stop(conn, &script_path, "org.kde.kwin.Script")?;

    let output = kwin_get_window_info(conn, window_id)?;
    print!("{}", output);

    Ok(())
}

fn get_user_filter() -> Option<String> {
    let status = fs::read_to_string("/proc/self/status").ok()?;
    for line in status.lines() {
        if line.starts_with("Uid:") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() > 1 {
                return Some(parts[1].to_string());
            }
        }
    }
    None
}

fn get_ancestors() -> Vec<u32> {
    let mut ancestors = Vec::new();
    let mut current_pid = std::process::id();

    while current_pid != 0 {
        ancestors.push(current_pid);
        let stat_path = format!("/proc/{}/stat", current_pid);
        if let Ok(stat) = fs::read_to_string(&stat_path) {
            // Format: pid (comm) state ppid ...
            // Find closing paren then get ppid
            if let Some(paren_end) = stat.rfind(')') {
                let after_comm = &stat[paren_end + 2..];
                let parts: Vec<&str> = after_comm.split_whitespace().collect();
                if parts.len() > 1 {
                    if let Ok(ppid) = parts[1].parse::<u32>() {
                        current_pid = ppid;
                        continue;
                    }
                }
            }
        }
        break;
    }

    ancestors
}

fn is_process_running(process: &str, user_filter: Option<&str>) -> bool {
    let ancestors = get_ancestors();
    let Ok(entries) = fs::read_dir("/proc") else {
        return false;
    };

    for entry in entries.flatten() {
        let path = entry.path();
        let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
            continue;
        };

        // Only process numeric directories (PIDs)
        let Ok(pid) = name.parse::<u32>() else {
            continue;
        };

        // Skip our own process and ancestors
        if ancestors.contains(&pid) {
            continue;
        }

        // Check user filter if specified
        if let Some(uid) = user_filter {
            let status_path = path.join("status");
            if let Ok(status) = fs::read_to_string(&status_path) {
                let mut matches_uid = false;
                for line in status.lines() {
                    if line.starts_with("Uid:") {
                        let parts: Vec<&str> = line.split_whitespace().collect();
                        if parts.len() > 1 && parts[1] == uid {
                            matches_uid = true;
                        }
                        break;
                    }
                }
                if !matches_uid {
                    continue;
                }
            } else {
                continue;
            }
        }

        // Check cmdline for process match
        let cmdline_path = path.join("cmdline");
        if let Ok(cmdline) = fs::read_to_string(&cmdline_path) {
            let cmdline = cmdline.replace('\0', " ");
            if cmdline.contains(process) {
                return true;
            }
        }
    }

    false
}

fn create_script(
    filter: &str,
    filter_alt: &str,
    filter_regex: &str,
    toggle: bool,
    center: Option<&str>,
    scale_factor: Option<f64>,
    max_aspect: Option<f64>,
    width: Option<&str>,
    height: Option<&str>,
    min_width: Option<&str>,
    max_width: Option<&str>,
    min_height: Option<&str>,
    max_height: Option<&str>,
    filter_focused: bool,
) -> Result<tempfile::NamedTempFile, String> {
    let content = build_script(
        filter, filter_alt, filter_regex, toggle, center,
        scale_factor, max_aspect, width, height,
        min_width, max_width, min_height, max_height, filter_focused,
    );

    let file = tempfile::NamedTempFile::new().map_err(|e| e.to_string())?;
    fs::write(file.path(), content).map_err(|e| e.to_string())?;
    Ok(file)
}

fn main() -> Result<(), String> {
    let args = Args::parse();
    let conn = get_connection()?;

    if args.info_active {
        return info_active(&conn);
    }

    let filter = args.filter.as_deref().unwrap_or("");
    let filter_alt = args.filter_alt.as_deref().unwrap_or("");
    let filter_regex = args.filter_regex.as_deref().unwrap_or("");

    if !args.filter_focused && filter.is_empty() && filter_alt.is_empty() && filter_regex.is_empty() {
        eprintln!("If you want that this program find a window, you need to specify a window filter — either by class (`-f`), by title (`-fa`), by regex (`-fr`), or use `--filter-focused`. More information can be seen if this script is called using the `--help` parameter.");
        std::process::exit(1);
    }

    let process = args
        .process
        .as_deref()
        .or(args.command.first().map(|s| s.as_str()))
        .unwrap_or("");

    let user_filter = if args.current_user {
        get_user_filter()
    } else {
        None
    };

    let is_running = if process.is_empty() {
        false
    } else {
        is_process_running(process, user_filter.as_deref())
    };

    // Helper closure to run a kwin script
    let run_script = |center: Option<&str>, toggle: bool| -> Result<(), String> {
        let script_file = create_script(
            filter,
            filter_alt,
            filter_regex,
            toggle,
            center,
            args.scale_factor,
            args.max_aspect,
            args.width.as_deref(),
            args.height.as_deref(),
            args.min_width.as_deref(),
            args.max_width.as_deref(),
            args.min_height.as_deref(),
            args.max_height.as_deref(),
            args.filter_focused,
        )?;
        let script_path = script_file.path().to_string_lossy();

        let random_name = format!("ww{}", rand::random::<u32>() % 10000);

        let id = kwin_load_script(&conn, &script_path, &random_name)?;

        let kwin_version = get_kwin_version(&conn)?;

        let (script_api_path, dbus_path) = if ver_between("5.21.90", &kwin_version, "5.27.79") {
            ("org.kde.kwin.Script", format!("/{}", id))
        } else if ver_lt("5.27.80", &kwin_version) {
            ("org.kde.kwin.Script", format!("/Scripting/Script{}", id))
        } else {
            ("org.kde.kwin.Scripting", format!("/{}", id))
        };

        let _ = kwin_script_run(&conn, &dbus_path, script_api_path);
        let _ = kwin_script_stop(&conn, &dbus_path, script_api_path);
        Ok(())
    };

    if is_running || args.filter_focused {
        // For "initial" mode, don't center when raising existing window
        let effective_center = if args.center.as_deref() == Some("initial") {
            None
        } else {
            args.center.as_deref()
        };
        run_script(effective_center, args.toggle)?;
    } else if !args.command.is_empty() {
        Command::new(&args.command[0])
            .args(&args.command[1..])
            .spawn()
            .map_err(|e| e.to_string())?;

        // For centering after spawn, operate on the now-active window
        if args.center.is_some() {
            std::thread::sleep(std::time::Duration::from_millis(500));
            let script_file = create_script(
                "", "", "", false, Some("always"),
                args.scale_factor, args.max_aspect,
                args.width.as_deref(), args.height.as_deref(),
                args.min_width.as_deref(), args.max_width.as_deref(),
                args.min_height.as_deref(), args.max_height.as_deref(),
                true, // filter_focused - operate on active window
            )?;
            let script_path = script_file.path().to_string_lossy();
            let random_name = format!("ww{}", rand::random::<u32>() % 10000);
            let id = kwin_load_script(&conn, &script_path, &random_name)?;
            let kwin_version = get_kwin_version(&conn)?;
            let (script_api_path, dbus_path) = if ver_between("5.21.90", &kwin_version, "5.27.79") {
                ("org.kde.kwin.Script", format!("/{}", id))
            } else if ver_lt("5.27.80", &kwin_version) {
                ("org.kde.kwin.Script", format!("/Scripting/Script{}", id))
            } else {
                ("org.kde.kwin.Scripting", format!("/{}", id))
            };
            let _ = kwin_script_run(&conn, &dbus_path, script_api_path);
            let _ = kwin_script_stop(&conn, &dbus_path, script_api_path);
        }
    }

    Ok(())
}
