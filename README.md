# programmableRouter

An interface for some pfSense functionality from Python.

## Setup

To use this library you'll need to disable CSRF protection in the pfSense  UI. This reduces the need for unnecessary requests to generate the tokens. To disable CSRF protection, edit `/usr/local/www/csrf/csrf-magic.php` and set `$GLOBALS['csrf']['defer']` to `true` (generally around line 26).