// 药品API测试脚本
console.log('🔵 开始测试药品API...')

// 测试获取药品列表
async function testMedicineAPI() {
  try {
    console.log('🔵 测试获取药品列表...')
    
    const response = await fetch('http://localhost:8000/api/medicines/')
    const data = await response.json()
    
    console.log('🟢 API响应:', {
      status: response.status,
      success: data.success,
      dataLength: Array.isArray(data.data) ? data.data.length : 'N/A',
      dataStructure: data.data ? Object.keys(data.data) : 'N/A'
    })
    
    if (data.success && Array.isArray(data.data)) {
      console.log('✅ 药品API测试成功！获取到', data.data.length, '个药品')
      if (data.data.length > 0) {
        console.log('📦 第一个药品:', {
          id: data.data[0].id,
          name: data.data[0].name,
          image_path: data.data[0].image_path
        })
      }
    } else {
      console.log('❌ 药品API响应格式异常')
      console.log('详细响应:', JSON.stringify(data, null, 2))
    }
    
  } catch (error) {
    console.error('🔴 药品API测试失败:', error.message)
  }
}

// 在浏览器控制台中运行测试
testMedicineAPI()