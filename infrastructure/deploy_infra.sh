#!/bin/bash

# 设置环境变量
ENVIRONMENT="prod"
REGION="cn-hangzhou"
STACK_NAME="book-management-system"

# 检查阿里云CLI是否安装
if ! command -v aliyun &> /dev/null
then
    echo "阿里云CLI未安装，请先安装: https://www.alibabacloud.com/help/zh/alibaba-cloud-command-line-interface"
    exit 1
fi

# 验证阿里云CLI配置
if ! aliyun configure get &> /dev/null
then
    echo "阿里云CLI未配置，请先运行: aliyun configure"
    exit 1
fi

# 创建资源栈
echo "创建资源栈: $STACK_NAME"
aliyun ros CreateStack \
  --StackName $STACK_NAME \
  --TemplateBody file://alicloud_ros.yaml \
  --Parameters "RegionId=$REGION,Environment=$ENVIRONMENT" \
  --TimeoutInMinutes 30 \
  --Capabilities CAPABILITY_NAMED_IAM

if [ $? -ne 0 ]; then
  echo "资源栈创建失败"
  exit 1
fi

# 等待栈创建完成
echo "等待资源栈创建完成..."
aliyun ros Wait StackCreateComplete \
  --StackName $STACK_NAME \
  --RegionId $REGION

if [ $? -ne 0 ]; then
  echo "资源栈创建过程中出错"
  exit 1
fi

# 获取输出
echo "资源栈创建完成，获取输出信息..."
aliyun ros GetStackResource \
  --StackName $STACK_NAME \
  --RegionId $REGION \
  --OutputType JSON \
  --query "Resources[?ResourceType == 'ALIYUN::FC::Function'].PhysicalResourceId" \
  --output json > outputs.json

# 解析输出
API_ENDPOINT=$(jq -r '.[0]' outputs.json)
FRONTEND_BUCKET=$(jq -r '.[1]' outputs.json)

echo "API网关地址: $API_ENDPOINT"
echo "前端存储桶: $FRONTEND_BUCKET"

# 创建前端环境配置文件
echo "创建前端环境配置文件..."
cat > frontend_env.js <<EOF
window.env = {
  VITE_API_BASE_URL: "$API_ENDPOINT"
};
EOF

echo "部署完成"