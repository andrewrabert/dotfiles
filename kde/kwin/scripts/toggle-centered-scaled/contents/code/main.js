// Parse resourceClasses - handle both StringList and newline-separated string
let rawClasses = readConfig("resourceClasses", ["tmux-scratchpad"]);
let resourceClasses = [];

if (Array.isArray(rawClasses)) {
    // If it's already an array, flatten any entries with newlines
    rawClasses.forEach(item => {
        if (typeof item === 'string') {
            item.split(/[\n,]/).forEach(part => {
                const trimmed = part.trim();
                if (trimmed.length > 0) {
                    resourceClasses.push(trimmed);
                }
            });
        }
    });
} else if (typeof rawClasses === 'string') {
    // If it's a string, split by newlines
    rawClasses.split(/[\n,]/).forEach(part => {
        const trimmed = part.trim();
        if (trimmed.length > 0) {
            resourceClasses.push(trimmed);
        }
    });
}

const maxAspect = readConfig("maxAspect", 1.6);
const scaleFactor = readConfig("scaleFactor", 0.8);

print("Scratchpad loaded: resourceClasses=[" + resourceClasses.join(", ") + "], maxAspect=" + maxAspect + ", scaleFactor=" + scaleFactor);

function isScratchpad(client) {
    if (!client || client.deleted || !client.normalWindow) {
        return false;
    }
    const resClass = client.resourceClass.toString();
    return resourceClasses.some(cls => resClass === cls.trim());
}

function findScratchpads() {
    let clients = workspace.windowList();
    return clients.filter(client => isScratchpad(client));
}

function findScratchpadsByClass(resClass) {
    let clients = workspace.windowList();
    return clients.filter(client => {
        if (!client || client.deleted || !client.normalWindow) {
            return false;
        }
        return client.resourceClass.toString() === resClass.trim();
    });
}

function findActiveScratchpadByClass(resClass) {
    let scratchpads = findScratchpadsByClass(resClass);
    return scratchpads.find(client => isVisible(client) && isActive(client)) || null;
}

function findVisibleScratchpadByClass(resClass) {
    let scratchpads = findScratchpadsByClass(resClass);
    return scratchpads.find(client => isVisible(client)) || null;
}

function findAnyScratchpadByClass(resClass) {
    let scratchpads = findScratchpadsByClass(resClass);
    return scratchpads.length > 0 ? scratchpads[0] : null;
}

function isVisible(client) {
    return !client.minimized;
}

function isActive(client) {
    return client === workspace.activeWindow;
}

function activate(client) {
    client.minimized = false;

    let activeScreen = workspace.activeScreen;
    let wsWidth = activeScreen.geometry.width;
    let wsHeight = activeScreen.geometry.height;
    if ((wsWidth / wsHeight) > maxAspect) {
        wsHeight = Math.min(wsWidth, wsHeight);
        wsWidth = wsHeight * maxAspect;
    }

    let width = wsWidth * scaleFactor;
    let height = wsHeight * scaleFactor;
    let x = (activeScreen.geometry.width - width) / 2;
    let y = (activeScreen.geometry.height - height) / 2;
    client.frameGeometry = {
        x: x,
        y: y,
        width: width,
        height: height
    };
    workspace.sendClientToScreen(client, activeScreen);
    workspace.activeWindow = client;
}

function setupClient(client) {
    configure_as_normal_window(client);
    hide(client);
    client.activeChanged.connect(function() {
        if (!client.active) {
            hide(client);
        }
    });
}

function configure_as_normal_window(client) {
    client.onAllDesktops = false;
    client.skipTaskbar = false;
    client.skipSwitcher = false;
    client.skipPager = false;
    client.keepAbove = false;
    client.fullScreen = false;

    client.minimized = false;
    client.fullScreen = false;
    client.noBorder = false;

}

function set_geometry_and_screen(client) {
    let activeScreen = workspace.screenAt(workspace.cursorPos);

    let wsWidth = activeScreen.geometry.width;
    let wsHeight = activeScreen.geometry.height;
    if ((wsWidth / wsHeight) > maxAspect) {
        wsHeight = Math.min(wsWidth, wsHeight);
        wsWidth = wsHeight * maxAspect;
    }

    let width = wsWidth * scaleFactor;
    let height = wsHeight * scaleFactor;
    let x = (activeScreen.geometry.width - width) / 2;
    let y = (activeScreen.geometry.height - height) / 2;
    client.frameGeometry = {
        x: x,
        y: y,
        width: width,
        height: height
    };
    workspace.sendClientToScreen(client, activeScreen);
}

function hide(client) {
    client.minimized = true;
    client.keepAbove = false;
}

function toggleScratchpad(resClass) {
    let activeScratchpad = findActiveScratchpadByClass(resClass);

    if (activeScratchpad) {
        // Active scratchpad is visible and focused - hide it
        hide(activeScratchpad);
    } else {
        // Check if any scratchpad is visible but not active
        let visibleScratchpad = findVisibleScratchpadByClass(resClass);
        if (visibleScratchpad) {
            // Activate the visible one
            set_geometry_and_screen(visibleScratchpad);
            activate(visibleScratchpad);
        } else {
            // No visible scratchpad - show any available one
            let scratchpad = findAnyScratchpadByClass(resClass);
            if (scratchpad) {
                set_geometry_and_screen(scratchpad);
                activate(scratchpad);
            }
        }
    }
}

function activateCurrentWindow() {
    let currentWindow = workspace.activeWindow;
    if (currentWindow && !currentWindow.deleted) {
        set_geometry_and_screen(currentWindow);
        activate(currentWindow);
    }
}

function showNormal() {
    let scratchpad = findAnyScratchpad();
    if (scratchpad) {
        configure_as_normal_window(scratchpad);
        activate(scratchpad);
    }
}

function setupScratchpad(client) {
    if (isScratchpad(client)) {
        setupClient(client);
    }
}

function init() {
    let scratchpads = findScratchpads();
    scratchpads.forEach(scratchpad => setupClient(scratchpad));

    workspace.windowAdded.connect(setupScratchpad);

    // Register a shortcut for each resource class
    resourceClasses.forEach((resClass, index) => {
        const trimmedClass = resClass.trim();
        const shortcutName = "Toggle " + trimmedClass;
        const shortcutDescription = "Toggle scratchpad for " + trimmedClass;
        const defaultShortcut = index === 0 ? "Meta+Return" : "";

        registerShortcut(shortcutName, shortcutDescription, defaultShortcut, function() {
            toggleScratchpad(trimmedClass);
        });

        print("Registered shortcut for " + trimmedClass);
    });

    // Register shortcut for activating current window
    registerShortcut("Activate Current Window", "Apply scratchpad geometry to current window", "", activateCurrentWindow);
    print("Registered shortcut for activating current window");
}

init();
