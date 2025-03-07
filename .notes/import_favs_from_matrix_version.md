# Removal of `favorites_import` Function

## Reason for Removal

The `favorites_import` function was originally included in the Rumble in the Jungle addon to facilitate the migration of user favorites from a previous addon, `plugin.video.rumble.matrix`. However, Rumble in the Jungle is a complete rewrite and should not rely on the original addon in any way. Furthermore, the function was found in the original project but was never assigned to a menu item, making it inaccessible to users. Since the migration is no longer needed, this function is being removed to streamline the codebase and avoid unnecessary dependencies.

## Function Being Removed

The following function is being removed but is documented here in case it needs to be reinstated in the future:

```python
import os
import xbmcgui
import xbmcvfs
import xbmc

def favorites_import():
    """
    Import favorites from the original 'plugin.video.rumble.matrix' addon to the current addon.

    This function is designed to migrate user favorites after a plugin name change from the original fork.
    It performs the following steps:
        1. Prompts the user for confirmation before proceeding with the import.
        2. Ensures the favorites directory for the current addon exists.
        3. Attempts to locate and read the favorites file from the original addon.
        4. If found, copies the content to the current addon's favorites file.
        5. Notifies the user of the import result.

    Returns:
        None

    Side effects:
        - May overwrite the current addon's favorites file.
        - Displays Kodi dialog boxes and notifications.

    Raises:
        No exceptions are explicitly raised, but file I/O operations may raise exceptions.
    """

    # Ask user for confirmation
    if not xbmcgui.Dialog().yesno(
            'Import Favorites',
            'This will replace the favorites with the plugin.video.rumble.matrix version.\nProceed?',
            nolabel='Cancel',
            yeslabel='Ok'):
        return

    # Ensure the current addon's favorites directory is created
    favorites_create()

    # Determine path to the old plugin's favorites file
    rumble_matrix_dir = xbmcvfs.translatePath(
        os.path.join('special://home/userdata/addon_data/plugin.video.rumble.matrix', 'favorites.dat')
    )

    # Check if the old file exists
    if not os.path.exists(rumble_matrix_dir):
        notify('Favorites Not Found')
        return

    try:
        # Safely read the old favorites file
        with open(rumble_matrix_dir, 'r', encoding='utf-8') as f:
            rumble_matrix = f.read()

        if not rumble_matrix:
            notify('Favorites Not Found')
            return

        # Write the content to the current addon's favorites file
        with open(favorites, 'w', encoding='utf-8') as fav_file:
            fav_file.write(rumble_matrix)

        notify('Imported Favorites')

    except Exception as e:
        # Optional logging for debug
        xbmc.log(f"[Favorites Import Error] {e}", level=xbmc.LOGERROR)
        notify('Favorites Import Failed')
```

## How to Restore This Function

If in the future it becomes necessary to reintroduce this function, follow these steps:

1. Copy the above function and paste it back into the appropriate module.
2. Ensure that the function `favorites_create()` is still defined, or add it back if needed.
3. Verify that `notify()` is available for displaying messages to the user.
4. If necessary, add a menu item or UI element in the Kodi addon to make the function accessible to users.
5. Test the function to ensure it correctly imports favorites from the old `plugin.video.rumble.matrix` addon.

By documenting this function here, future maintainers can quickly restore its functionality if needed while maintaining a clean and efficient codebase.

