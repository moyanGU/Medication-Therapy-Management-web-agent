import axios from 'axios';

const USERNAME = process.env.TEST_USERNAME;
const PASSWORD = process.env.TEST_PASSWORD;

if (!USERNAME || !PASSWORD) {
  console.error('请通过环境变量TEST_USERNAME/TEST_PASSWORD提供账号密码');
  process.exit(2);
}

async function testLogin() {
  try {
    console.log('测试登录API...');

    const response = await axios.post('http://localhost:8000/api/auth/login/', {
      username: USERNAME,
      password: PASSWORD
    }, {
      headers: { 'Content-Type': 'application/json' }
    });

    console.log('登录响应状态:', response.status);
    console.log('登录响应数据:', JSON.stringify(response.data, null, 2));

    const d = response.data?.data || response.data;
    const token = d?.access_token || d?.token || d?.access || d?.tokens?.access || null;
    const refresh = d?.refresh_token || d?.refresh || d?.tokens?.refresh || null;

    if (!token) {
      throw new Error('未在响应中找到token字段(access_token/token/access/tokens.access)');
    }

    console.log('TOKEN长度:', token.length);
    console.log('TOKEN前缀:', token.substring(0, Math.min(12, token.length)));
    console.log('REFRESH存在:', !!refresh);
    console.log('建议Authorization头:');
    console.log(`Bearer ${token}`);

    return token;
  } catch (error) {
    console.error('登录测试失败:');
    if (error.response) {
      console.log('状态码:', error.response.status);
      console.log('错误数据:', JSON.stringify(error.response.data, null, 2));
      if (error.response.status === 401) {
        console.log('🔒 认证失败 - 请检查用户名/密码');
      }
    } else if (error.request) {
      console.log('请求已发出但无响应:', error.message);
    } else {
      console.log('错误信息:', error.message);
    }
    throw error;
  }
}

async function testProfile(authToken) {
  try {
    console.log('\n测试获取用户信息 API...');
    const resp = await axios.get('http://localhost:8000/api/user/profile/', {
      headers: { Authorization: `Bearer ${authToken}` }
    });

    console.log('Profile响应状态:', resp.status);
    console.log('Profile响应数据:', JSON.stringify(resp.data, null, 2));

    const inner = resp.data?.data || resp.data;
    if (!inner) throw new Error('响应缺少data字段');

    const keys = typeof inner === 'object' ? Object.keys(inner) : [];
    console.log('Profile字段:', keys.join(', '));

    return inner;
  } catch (error) {
    console.error('获取用户信息失败:');
    if (error.response) {
      console.log('状态码:', error.response.status);
      console.log('错误数据:', JSON.stringify(error.response.data, null, 2));
    } else {
      console.log('错误信息:', error.message);
    }
    throw error;
  }
}

async function main() {
  console.log('开始API测试...\n');
  const token = await testLogin();
  await testProfile(token);
  console.log('\n测试完成');
}

main().catch(() => process.exit(1));