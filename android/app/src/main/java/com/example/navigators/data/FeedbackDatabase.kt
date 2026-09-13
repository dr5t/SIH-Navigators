package com.example.navigators.data

import android.content.Context
import androidx.room.*

@Entity(tableName = "feedback_queue")
data class FeedbackEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val category: String,
    val description: String,
    val severity: String,
    val sessionId: String?,
    val technicalContextJson: String?,
    val rating: String?
)

@Dao
interface FeedbackDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insert(feedback: FeedbackEntity)
    
    @Query("SELECT * FROM feedback_queue ORDER BY id ASC")
    fun getAll(): List<FeedbackEntity>
    
    @Query("DELETE FROM feedback_queue WHERE id IN (:ids)")
    fun deleteByIds(ids: List<Int>)
}

@Database(entities = [FeedbackEntity::class], version = 1, exportSchema = false)
abstract class FeedbackDatabase : RoomDatabase() {
    abstract fun feedbackDao(): FeedbackDao

    companion object {
        @Volatile
        private var INSTANCE: FeedbackDatabase? = null

        fun getDatabase(context: Context): FeedbackDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    FeedbackDatabase::class.java,
                    "feedback_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
