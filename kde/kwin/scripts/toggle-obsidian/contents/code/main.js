function isObsidian(client) {
    return client && !client.deleted && client.normalWindow && client.resourceClass.toString() === "obsidian";
}

function findObsidian() {
    let clients = workspace.windowList();
    return clients.find(client => isObsidian(client)) || null;
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
        if (!isNormal && !client.active) {
            hide(client);
        }
    });
}

const maxAspect = 1.6;
const scaleFactor = 0.8;


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

function toggleObsidian() {
    let obsidian = findObsidian();
    if (obsidian) {
        if (isVisible(obsidian)) {
            if (isActive(obsidian)) {
                hide(obsidian);
            } else {
                set_geometry_and_screen(obsidian);
                activate(obsidian);
            }
        } else {
            set_geometry_and_screen(obsidian);
            activate(obsidian);
        }
    }
}

function showNormal() {
    let obsidian = findObsidian();
    if (obsidian) {
        configure_as_normal_window(obsidian);
        activate(obsidian);
    }
}

function setupObsidian(client) {
    if (isObsidian(client)) {
        setupClient(client);
    }
}

function init() {
    let obsidian = findObsidian();
    if (obsidian) {
        setupClient(obsidian);
    }

    workspace.windowAdded.connect(setupObsidian);
    registerShortcut("Obsidian Toggle", "Toggle Obsidian.", "Meta+n", toggleObsidian);
}

init();
