# Add project specific ProGuard rules here.
# By default, the flags in this file are applied to
# all build variants.

# ProGuard rules for Library Projects.
#
# General best practices:
# - Using -keepclassmembers only on classes with public methods is not enough.
#   Even if a library class has only public methods, it can be removed if it is
#   not used by the main dex file.
# - Using -keep for every class in the library is not a good solution, since it
#   will bloat the app.
# - Instead, use -keepclassmembers on all public and protected members of public
#   classes, and on all public and protected constructors of public classes.

# Add any project specific keep rules here:

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# If you use Gson, uncomment the following line:
#-keep class com.google.gson.examples.android.model.** { *; }

# If you use retrofit, uncomment the following line
#-keep class * extends retrofit.converter.Converter

# If you use Picasso, uncomment the following line
#-dontwarn com.squareup.okhttp.**

# If you use okhttp, uncomment the following line
#-keep class okhttp3.** { *; }
#-keep interface okhttp3.** { *; }
#-dontwarn okhttp3.**
#-dontwarn okio.**

# If you use Joda Time, uncomment the following line
#-keep class org.joda.time.** { *; }
#-keep interface org.joda.time.** { *; }
#-dontwarn org.joda.time.**

# If you use google-play-services, uncomment the following:
#-keep class * extends java.util.ListResourceBundle {
#    protected Object[][] getContents();
#}

# If you use an enum with a custom value, uncomment the following:
#-keepclassmembers enum * {
#    public static **[] values();
#    public static ** valueOf(java.lang.String);
#}