package com.example.navigators

import android.app.Application
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class NavigatorsApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        org.osmdroid.config.Configuration.getInstance().apply {
            // App-private persistent tile storage: no external-storage permission required.
            osmdroidBasePath = java.io.File(filesDir, "maps").apply { mkdirs() }
            osmdroidTileCache = java.io.File(osmdroidBasePath, "tiles").apply { mkdirs() }
            userAgentValue = "com.example.navigators/1.0"
            tileFileSystemCacheMaxBytes = 128L * 1024 * 1024
            tileFileSystemCacheTrimBytes = 96L * 1024 * 1024
            tileDownloadThreads = 2
            tileDownloadMaxQueueSize = 32
            cacheMapTileCount = 64
        }
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
    }
}
