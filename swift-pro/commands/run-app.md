---
description: Build and launch on simulator
allowed-tools: Bash, Read, Grep, Glob
---

# Run App on Simulator

Build the project and launch it on an iOS Simulator.

## Step 1: Discover the Project

```bash
find . -maxdepth 3 -name "*.xcworkspace" -not -path "*/Pods/*" -not -path "*/.build/*" | head -5
find . -maxdepth 3 -name "*.xcodeproj" | head -5
```

Identify the main app scheme (not test schemes).

## Step 2: List Available Simulators

```bash
xcrun simctl list devices available --json 2>/dev/null | head -80
```

Pick the best simulator:
1. If an iPhone 16 Pro is available and booted, use it
2. If no simulator is booted, prefer iPhone 16 or iPhone 16 Pro
3. Fall back to any available iOS simulator

## Step 3: Boot the Simulator (if needed)

```bash
# Check if target simulator is booted
xcrun simctl list devices booted

# Boot if needed
xcrun simctl boot "<Device UDID>"
```

## Step 4: Build the App

```bash
xcodebuild build \
  -workspace <Workspace>.xcworkspace \
  -scheme <Scheme> \
  -destination "platform=iOS Simulator,id=<Device UDID>" \
  -derivedDataPath build/ \
  -quiet 2>&1
```

If the build fails, report errors and stop. Do not attempt to install a failed build.

## Step 5: Install the App

Find the built .app bundle and install it:

```bash
# Find the .app
find build/Build/Products -name "*.app" -maxdepth 3 | head -1

# Install
xcrun simctl install "<Device UDID>" "<path-to-.app>"
```

## Step 6: Launch the App

```bash
# Get the bundle identifier from the app's Info.plist
/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "<path-to-.app>/Info.plist"

# Launch
xcrun simctl launch "<Device UDID>" <bundle-identifier>
```

## Step 7: Screenshot (Optional)

If the user requested a screenshot or if you want to verify the launch:

```bash
# Wait for app to render
sleep 2

# Take screenshot
xcrun simctl io "<Device UDID>" screenshot app_screenshot.png
```

## Report

Summarize:
- Simulator used (device name and OS version)
- Build result
- App bundle identifier
- Launch status
- Screenshot path (if taken)
