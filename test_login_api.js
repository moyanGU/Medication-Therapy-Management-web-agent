import axios from 'axios';

// 测试登录API
async function testLogin() {
  try {
    console.log('测试登录API...');
    
    // 测试登录请求
    const response = await axios.post('http://localhost:8000/api/auth/login/', {
      username: 'testuser',
      password: 'test123456'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('登录响应状态:', response.status);
    console.log('登录响应数据:', JSON.stringify(response.data, null, 2));
    
    // 检查响应结构
    if (response.data && response.data.success !== undefined) {
      console.log('✅ API响应包含success字段:', response.data.success);
    } else {
      console.log('❌ API响应缺少success字段');
    }
    
    if (response.data && response.data.data) {
      console.log('✅ API响应包含data字段');
      
      // 检查data字段的结构
      const data = response.data.data;
      console.log('data字段结构:', Object.keys(data));
      
      // 检查可能的token字段
      if (data.access_token || data.tokens || data.access) {
        console.log('✅ 找到token相关字段');
      } else {
        console.log('❌ 未找到token相关字段');
      }
      
    } else {
      console.log('❌ API响应缺少data字段');
    }
    
  } catch (error) {
    console.error('登录测试失败:');
    
    if (error.response) {
      // 服务器返回错误响应
      console.log('状态码:', error.response.status);
      console.log('错误数据:', JSON.stringify(error.response.data, null, 2));
      
      // 检查401错误的具体信息
      if (error.response.status === 401) {
        console.log('🔒 认证失败 - 需要有效的用户名密码');
      }
      
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.log('请求已发出但无响应:', error.message);
    } else {
      // 其他错误
      console.log('错误信息:', error.message);
    }
  }
}

// 测试获取药品列表（需要认证）
async function testMedicines(authToken = null) {
  try {
    console.log('\n测试药品列表API...');
    
    const config = authToken ? {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    } : {};
    
    const response = await axios.get('http://localhost:8000/api/medicines/', config);
    
    console.log('药品列表响应状态:', response.status);
    console.log('药品列表响应结构:', JSON.stringify(response.data, null, 2));
    
    // 检查双重data结构
    if (response.data && response.data.data) {
      const innerData = response.data.data;
      console.log('内层data类型:', typeof innerData);
      
      if (Array.isArray(innerData)) {
        console.log('✅ 内层data是数组，长度:', innerData.length);
      } else if (innerData && typeof innerData === 'object') {
        console.log('✅ 内层data是对象，包含字段:', Object.keys(innerData));
      }
    }
    
  } catch (error) {
    console.error('药品列表测试失败:');
    
    if (error.response) {
      console.log('状态码:', error.response.status);
      console.log('错误信息:', error.response.data?.message || error.response.data);
      
      if (error.response.status === 401) {
        console.log('🔒 需要有效的认证token');
      }
      
    } else {
      console.log('错误信息:', error.message);
    }
  }
}

// 主测试函数
async function main() {
  console.log('开始API测试...\n');
  
  // 首先测试登录
  await testLogin();
  
  // 如果登录成功，可以继续测试需要认证的接口
  // 这里先注释掉，等登录成功后再测试
  // await testMedicines('your_token_here');
  
  console.log('\n测试完成');
}

// 运行测试
main().catch(console.error);