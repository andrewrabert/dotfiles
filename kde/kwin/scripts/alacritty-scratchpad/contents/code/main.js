function isAlacritty(client) {
    return client && !client.deleted && client.normalWindow && client.resourceClass.toString() === "tmux-scratchpad";
}

function findAlacritty() {
    let clients = workspace.windowList();
    return clients.find(client => isAlacritty(client)) || null;
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
    configure_as_floating_window(client);
    hide(client);
    client.activeChanged.connect(function() {
        if (!isNormal && !client.active) {
            hide(client);
        }
    });
}

const maxAspect = 1.6;
const scaleFactor = 0.8;
let isNormal = false;


function configure_as_normal_window(client) {
    isNormal = true;

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

function configure_as_floating_window(client) {
    isNormal = false;

    client.noBorder = true;
    client.skipTaskbar = true;
    client.skipSwitcher = true;
    client.skipPager = true;
    client.onAllDesktops = true;
    client.fullScreen = false;
    client.keepAbove = true;
}

function hide(client) {
    client.minimized = true;
    client.keepAbove = false;
}

function toggleAlacritty() {
    let alacritty = findAlacritty();
    if ( alacritty ) {
        if ( isNormal ) {
            set_geometry_and_screen(alacritty);
            configure_as_floating_window(alacritty);
            activate(alacritty);
        } else if ( isVisible(alacritty) ) {
            if ( isActive(alacritty) ) {
                hide(alacritty);
            } else {
                set_geometry_and_screen(alacritty);
                activate(alacritty);
            }
        } else {
            set_geometry_and_screen(alacritty);
            configure_as_floating_window(alacritty);
            activate(alacritty);
        }
    }
}

function showNormal() {
    let alacritty = findAlacritty();
    if ( alacritty ) {
        configure_as_normal_window(alacritty);
        activate(alacritty);
    }
}

function setupAlacritty(client) {
    if ( isAlacritty(client) ) {
        setupClient(client);
    }
}

function init() {
    let alacritty = findAlacritty();
    if ( alacritty ) {
        setupClient(alacritty);
    }

    workspace.windowAdded.connect(setupAlacritty);
    registerShortcut("Scratchpad Toggle", "Toggle scratchpad.", "Meta+Return", toggleAlacritty);
    registerShortcut("Show Window", "Show scratchpad as a normal window.", "Shift+Meta+Return", showNormal);
}

init();
