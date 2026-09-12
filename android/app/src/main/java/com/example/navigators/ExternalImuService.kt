package com.example.navigators

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothProfile
import android.content.Context
import android.util.Log
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.UUID

class ExternalImuService(private val context: Context, private val deviceAddress: String) {
    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private var bluetoothGatt: BluetoothGatt? = null
    
    // Example UUIDs for a generic BLE IMU (e.g. Nordic UART Service or custom)
    private val IMU_SERVICE_UUID = UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    private val IMU_CHARACTERISTIC_UUID = UUID.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

    // Callback to pass data back to Python engine: accel(3), gyro(3), timestamp
    var onExternalImuData: ((FloatArray, FloatArray, Long) -> Unit)? = null

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i("ExternalImuService", "Connected to BLE IMU")
                gatt.discoverServices()
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.i("ExternalImuService", "Disconnected from BLE IMU")
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                val service = gatt.getService(IMU_SERVICE_UUID)
                val characteristic = service?.getCharacteristic(IMU_CHARACTERISTIC_UUID)
                if (characteristic != null) {
                    gatt.setCharacteristicNotification(characteristic, true)
                }
            }
        }

        override fun onCharacteristicChanged(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic) {
            if (characteristic.uuid == IMU_CHARACTERISTIC_UUID) {
                parseImuPayload(characteristic.value)
            }
        }
    }

    fun connect() {
        if (bluetoothAdapter == null) return
        val device: BluetoothDevice = bluetoothAdapter.getRemoteDevice(deviceAddress)
        // Note: requires BLUETOOTH_CONNECT permission on Android 12+
        try {
            bluetoothGatt = device.connectGatt(context, false, gattCallback)
        } catch (e: SecurityException) {
            Log.e("ExternalImuService", "Missing Bluetooth permissions", e)
        }
    }

    fun disconnect() {
        try {
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
        } catch (e: SecurityException) {
             Log.e("ExternalImuService", "Missing Bluetooth permissions", e)
        }
    }

    private fun parseImuPayload(payload: ByteArray) {
        // Assuming 24-byte payload: 6 floats (ax, ay, az, gx, gy, gz)
        if (payload.size >= 24) {
            val buffer = ByteBuffer.wrap(payload).order(ByteOrder.LITTLE_ENDIAN)
            val accel = FloatArray(3)
            val gyro = FloatArray(3)
            
            accel[0] = buffer.float
            accel[1] = buffer.float
            accel[2] = buffer.float
            
            gyro[0] = buffer.float
            gyro[1] = buffer.float
            gyro[2] = buffer.float
            
            val timestamp = System.nanoTime() // Align to local Android clock
            
            onExternalImuData?.invoke(accel, gyro, timestamp)
        }
    }
}
