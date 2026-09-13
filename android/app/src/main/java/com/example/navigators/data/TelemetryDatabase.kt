package com.example.navigators.data

import android.content.Context
import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.Insert
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.Room
import androidx.room.RoomDatabase

@Entity(tableName = "telemetry_queue")
data class TelemetryEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val sessionId: String,
    val timestamp: Long,
    val lat: Double,
    val lon: Double,
    val alt: Double,
    val speed: Double,
    val course: Double,
    val hAcc: Double,
    val vAcc: Double,
    val mode: String
)

@Dao
interface TelemetryDao {
    @Insert
    fun insert(telemetry: TelemetryEntity)

    @Insert
    fun insertAll(telemetryList: List<TelemetryEntity>)

    @Query("SELECT * FROM telemetry_queue ORDER BY timestamp ASC LIMIT :limit")
    fun getOldest(limit: Int): List<TelemetryEntity>

    @Query("DELETE FROM telemetry_queue WHERE id IN (:ids)")
    fun deleteByIds(ids: List<Int>)
    
    @Query("DELETE FROM telemetry_queue")
    fun clearAll()
    
    @Query("SELECT COUNT(*) FROM telemetry_queue")
    fun count(): Int
}

@Database(entities = [TelemetryEntity::class], version = 2, exportSchema = false)
abstract class TelemetryDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao

    companion object {
        @Volatile
        private var INSTANCE: TelemetryDatabase? = null

        fun getDatabase(context: Context): TelemetryDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    TelemetryDatabase::class.java,
                    "navigators_telemetry.db"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
