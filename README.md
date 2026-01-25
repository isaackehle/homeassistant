# Home Assistant Blueprints

A curated collection of blueprints for [Home Assistant](https://www.home-assistant.io/). These blueprints provide ready-to-use automations and scripts that you can easily import and customize for your smart home.

## 📋 Available Blueprints

### Automations

#### 💡 Lighting
- **[Motion-activated Light](blueprints/automation/lighting/motion-activated-light.yaml)** - Automatically turn lights on when motion is detected and off after a configurable delay. Includes optional illuminance threshold support.

#### 🔒 Security
- **[Door/Window Monitor](blueprints/automation/security/door-window-monitor.yaml)** - Monitor door and window sensors with instant notifications when opened. Optional reminders if left open too long.

### Scripts

#### 📱 Notifications
- **[Smart Notification Center](blueprints/script/notifications/smart-notification-center.yaml)** - A flexible notification system supporting mobile notifications, TTS announcements, and persistent notifications with priority levels.

## 🚀 How to Use

### Method 1: Import via URL (Recommended)

1. In Home Assistant, go to **Settings** → **Automations & Scenes**
2. Click the **Blueprints** tab
3. Click **Import Blueprint** (bottom right)
4. Paste the raw URL of the blueprint you want to use:
   ```
   https://raw.githubusercontent.com/isaackehle/homeassistant-blueprints/main/blueprints/automation/lighting/motion-activated-light.yaml
   ```
5. Click **Preview Blueprint** and then **Import Blueprint**
6. The blueprint is now available to use in your automations

### Method 2: Manual Installation

1. Navigate to your Home Assistant configuration directory
2. Create the blueprint directory structure if it doesn't exist:
   ```bash
   mkdir -p blueprints/automation
   mkdir -p blueprints/script
   ```
3. Copy the desired blueprint YAML file to the appropriate directory
4. Restart Home Assistant or reload automations
5. The blueprint will appear in your automations list

## 📝 Blueprint Details

Each blueprint includes:
- **Clear description** of what it does
- **Configurable inputs** with sensible defaults
- **Input validation** using selectors
- **Minimum Home Assistant version** requirements
- **Comprehensive documentation** within the YAML file

## 🤝 Contributing

Contributions are welcome! If you have a blueprint you'd like to share:

1. Fork this repository
2. Create a new branch for your blueprint
3. Add your blueprint to the appropriate category
4. Update this README with a link to your blueprint
5. Submit a pull request

Please ensure your blueprints:
- Follow the Home Assistant [blueprint schema](https://www.home-assistant.io/docs/blueprint/schema/)
- Include clear descriptions and documentation
- Use appropriate selectors for inputs
- Are tested and working

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [Home Assistant Documentation](https://www.home-assistant.io/)
- [Blueprint Documentation](https://www.home-assistant.io/docs/blueprint/)
- [Blueprint Schema Reference](https://www.home-assistant.io/docs/blueprint/schema/)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

## 💬 Support

If you have questions or need help:
- Open an issue in this repository
- Visit the [Home Assistant Community Forum](https://community.home-assistant.io/)
- Check the [Home Assistant Discord](https://discord.gg/home-assistant)

---

**Note**: These blueprints are provided as-is. Always test in a safe environment before deploying to your production Home Assistant instance.