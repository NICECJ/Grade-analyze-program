<template>
  <div class="standard-template-import">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>标准模板导入</span>
          <el-button type="text" @click="showTemplateHelp = true">
            <el-icon><QuestionFilled /></el-icon>
            模板说明
          </el-button>
        </div>
      </template>

      <!-- 导入表单 -->
      <el-form :model="importForm" :rules="rules" ref="importFormRef" label-width="120px">
        <el-form-item label="考试名称" prop="exam_name">
          <el-input v-model="importForm.exam_name" placeholder="请输入考试名称" />
        </el-form-item>
        
        <el-form-item label="考试日期" prop="exam_date">
          <el-date-picker
            v-model="importForm.exam_date"
            type="datetime"
            placeholder="选择考试日期"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        
        <el-form-item label="考试类型" prop="exam_type">
          <el-radio-group v-model="importForm.exam_type" @change="onExamTypeChange">
            <el-radio label="物理类">物理类</el-radio>
            <el-radio label="历史类">历史类</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="考试级别" prop="exam_level">
          <el-select v-model="importForm.exam_level" placeholder="选择考试级别">
            <el-option label="校级考试" value="校级" />
            <el-option label="市级考试" value="市级" />
            <el-option label="省级考试" value="省级" />
          </el-select>
        </el-form-item>

        <el-form-item label="选科组合" prop="subject_combination">
          <el-select v-model="importForm.subject_combination" placeholder="选择选科组合（可选）">
            <el-option label="不指定（根据数据自动识别）" value="" />
            <el-optgroup label="物理类组合">
              <el-option label="物化生（物理+化学+生物）" value="物化生" />
              <el-option label="物化地（物理+化学+地理）" value="物化地" />
              <el-option label="物化政（物理+化学+政治）" value="物化政" />
              <el-option label="物生地（物理+生物+地理）" value="物生地" />
              <el-option label="物生政（物理+生物+政治）" value="物生政" />
              <el-option label="物地政（物理+地理+政治）" value="物地政" />
            </el-optgroup>
            <el-optgroup label="历史类组合">
              <el-option label="史化生（历史+化学+生物）" value="史化生" />
              <el-option label="史化地（历史+化学+地理）" value="史化地" />
              <el-option label="史化政（历史+化学+政治）" value="史化政" />
              <el-option label="史生地（历史+生物+地理）" value="史生地" />
              <el-option label="史生政（历史+生物+政治）" value="史生政" />
              <el-option label="史地政（历史+地理+政治）" value="史地政" />
            </el-optgroup>
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 模板下载 -->
      <el-alert
        title="使用标准模板可以快速导入，无需手动映射字段"
        type="info"
        :closable="false"
        style="margin: 20px 0;"
      >
        <div style="margin-top: 10px;">
          <el-button type="primary" size="small" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载{{ importForm.exam_type }}标准模板
          </el-button>
          <el-button type="text" size="small" @click="previewTemplate">
            预览模板格式
          </el-button>
        </div>
      </el-alert>

      <!-- 文件上传 -->
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将标准模板Excel文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请使用标准模板格式，只能上传 .xlsx/.xls 文件
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="file-info">
        <p><strong>已选择文件:</strong> {{ selectedFile.name }}</p>
        <el-button 
          type="primary" 
          @click="importData" 
          :loading="importLoading"
          :disabled="!canImport"
        >
          开始导入
        </el-button>
      </div>

      <!-- 导入结果 -->
      <div v-if="importResult" class="import-result">
        <el-result
          icon="success"
          title="导入成功!"
          :sub-title="`检测类型: ${importResult.detected_type}, 导入学生: ${importResult.imported_students}人, 成绩记录: ${importResult.imported_grades}条`"
        >
          <template #extra>
            <el-button @click="resetForm">重新导入</el-button>
            <el-button type="primary" @click="viewExamAnalysis">
              查看考试分析
            </el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 模板说明对话框 -->
    <el-dialog v-model="showTemplateHelp" title="标准模板说明" width="800px">
      <div class="template-help">
        <h3>标准模板格式说明</h3>
        <p>标准模板采用固定的列名格式，系统会自动识别和导入数据。</p>
        
        <h4>必需字段：</h4>
        <ul>
          <li><strong>姓名</strong> - 学生姓名（必填）</li>
          <li><strong>学校</strong> - 所属学校</li>
          <li><strong>班级</strong> - 所在班级（必填，作为学生标识）</li>
          <li><strong>年级</strong> - 年级信息</li>
        </ul>

        <h4>成绩字段：</h4>
        <div class="subject-info">
          <div class="subject-group">
            <h5>物理类包含：</h5>
            <p><strong>必修：</strong>语文、数学、英语、物理（仅原始成绩）</p>
            <p><strong>选考（四选二）：</strong>化学、生物、地理、政治</p>
            <p style="margin-left: 20px; color: #666;">可任意选择2门，未选择的科目留空即可</p>
            <p style="margin-left: 20px; color: #666;">格式：科目 → 科目赋分 → 排名信息</p>
            <p><strong>总分：</strong>原始总分 → 赋分总分 → 排名信息</p>
          </div>
          <div class="subject-group">
            <h5>历史类包含：</h5>
            <p><strong>必修：</strong>语文、数学、英语、历史（仅原始成绩）</p>
            <p><strong>选考（四选二）：</strong>化学、生物、地理、政治</p>
            <p style="margin-left: 20px; color: #666;">可任意选择2门，未选择的科目留空即可</p>
            <p style="margin-left: 20px; color: #666;">格式：科目 → 科目赋分 → 排名信息</p>
            <p><strong>总分：</strong>原始总分 → 赋分总分 → 排名信息</p>
          </div>
        </div>

        <h4>选课组合说明：</h4>
        <div class="combination-info">
          <p><strong>常见组合示例：</strong></p>
          <ul>
            <li><strong>物理类：</strong>物化生、物化地、物化政、物生地、物生政、物地政</li>
            <li><strong>历史类：</strong>史化生、史化地、史化政、史生地、史生政、史地政</li>
          </ul>
          <p style="color: #E6A23C;"><strong>注意：</strong>模板包含所有四个选考科目的列，根据实际选课情况填写，未选择的科目列可以留空。</p>
        </div>

        <h4>列顺序说明：</h4>
        <div class="column-order-example">
          <p><strong>选考科目列顺序：</strong></p>
          <div class="order-example">
            <span class="step">1. 化学</span>
            <span class="arrow">→</span>
            <span class="step">2. 化学赋分</span>
            <span class="arrow">→</span>
            <span class="step">3. 化学校排名</span>
            <span class="arrow">→</span>
            <span class="step">4. 化学市排名</span>
            <span class="arrow">→</span>
            <span class="step">5. 化学省排名</span>
            <span class="arrow">→</span>
            <span class="step">6. 化学赋分校排名</span>
            <span class="arrow">→</span>
            <span class="step">7. 化学赋分市排名</span>
            <span class="arrow">→</span>
            <span class="step">8. 化学赋分省排名</span>
          </div>
        </div>

        <h4>排名字段（可选）：</h4>
        <p>每个科目可以包含对应的排名信息：</p>
        <ul>
          <li><strong>原始成绩排名：</strong>科目名+校排名/市排名/省排名（如：语文校排名）</li>
          <li><strong>赋分成绩排名：</strong>科目名+赋分+校排名/市排名/省排名（如：化学赋分校排名）</li>
        </ul>

        <h4>赋分科目说明：</h4>
        <ul>
          <li><strong>物理类：</strong>化学、生物、地理、政治需要赋分</li>
          <li><strong>历史类：</strong>化学、生物、地理、政治需要赋分</li>
          <li><strong>总分：</strong>包含赋分后的总分计算</li>
          <li>赋分科目需要同时提供原始成绩和赋分成绩</li>
        </ul>

        <h4>注意事项：</h4>
        <ul>
          <li>请严格按照模板格式填写，列名不能修改</li>
          <li>学生以"学校+班级+姓名"作为唯一标识</li>
          <li>成绩可以为空，但姓名和班级不能为空</li>
          <li>排名信息为可选，可以只填写部分排名</li>
          <li><strong>选考科目：</strong>根据学生实际选课填写，未选择的科目整列留空</li>
          <li><strong>赋分科目：</strong>选考科目需要同时提供原始成绩和赋分成绩</li>
          <li><strong>总分：</strong>需要提供原始总分和赋分总分</li>
          <li>赋分成绩通常在原始成绩基础上进行等级转换</li>
          <li><strong>文件格式：</strong>下载的是CSV格式，可以用Excel打开编辑，保存时选择Excel格式(.xlsx)</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 模板预览对话框 -->
    <el-dialog v-model="showTemplatePreview" title="模板预览" width="1000px">
      <div v-if="templatePreview">
        <p><strong>{{ templatePreview.exam_type }}标准模板格式：</strong></p>
        <el-table :data="templatePreview.sample_data" style="width: 100%" max-height="400">
          <el-table-column
            v-for="col in templatePreview.columns"
            :key="col"
            :prop="col"
            :label="col"
            width="100"
            show-overflow-tooltip
          />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'StandardTemplateImport',
  data() {
    return {
      importForm: {
        exam_name: '',
        exam_date: '',
        exam_type: '物理类',
        exam_level: '校级',
        subject_combination: ''
      },
      rules: {
        exam_name: [
          { required: true, message: '请输入考试名称', trigger: 'blur' }
        ],
        exam_date: [
          { required: true, message: '请选择考试日期', trigger: 'change' }
        ],
        exam_type: [
          { required: true, message: '请选择考试类型', trigger: 'change' }
        ],
        exam_level: [
          { required: true, message: '请选择考试级别', trigger: 'change' }
        ]
      },
      selectedFile: null,
      importLoading: false,
      importResult: null,
      showTemplateHelp: false,
      showTemplatePreview: false,
      templatePreview: null
    }
  },
  computed: {
    canImport() {
      return this.selectedFile && 
             this.importForm.exam_name && 
             this.importForm.exam_date && 
             this.importForm.exam_type && 
             this.importForm.exam_level
    }
  },
  methods: {
    handleFileChange(file) {
      this.selectedFile = file.raw
      this.importResult = null
    },

    onExamTypeChange() {
      // 考试类型改变时清空已选文件，提醒用户重新下载模板
      if (this.selectedFile) {
        this.$confirm('考试类型已改变，建议重新下载对应的标准模板。是否清空当前文件？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.selectedFile = null
          this.$refs.uploadRef.clearFiles()
        })
      }
    },

    async downloadTemplate() {
      try {
        // 转换中文考试类型为英文枚举值
        const examTypeMap = {
          '物理类': 'PHYSICS',
          '历史类': 'HISTORY'
        }
        const examTypeEnum = examTypeMap[this.importForm.exam_type]
        
        const response = await api.exams.getTemplateExample(examTypeEnum)
        
        // 创建CSV格式下载（不依赖XLSX库）
        const headers = response.columns
        const rows = response.sample_data
        
        // 构建CSV内容
        let csvContent = headers.join(',') + '\n'
        rows.forEach(row => {
          const values = headers.map(header => {
            const value = row[header] || ''
            // 如果值包含逗号或引号，需要用引号包围
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
              return `"${value.replace(/"/g, '""')}"`
            }
            return value
          })
          csvContent += values.join(',') + '\n'
        })
        
        // 创建Blob并下载
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `${this.importForm.exam_type}标准模板.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        this.$message.success('模板下载成功（CSV格式）')
      } catch (error) {
        this.$message.error('模板下载失败: ' + (error.response?.data?.detail || error.message))
      }
    },

    async previewTemplate() {
      try {
        // 转换中文考试类型为英文枚举值
        const examTypeMap = {
          '物理类': 'PHYSICS',
          '历史类': 'HISTORY'
        }
        const examTypeEnum = examTypeMap[this.importForm.exam_type]
        
        this.templatePreview = await api.exams.getTemplateExample(examTypeEnum)
        this.showTemplatePreview = true
      } catch (error) {
        this.$message.error('模板预览失败: ' + (error.response?.data?.detail || error.message))
      }
    },

    async importData() {
      if (!this.$refs.importFormRef) return
      
      const valid = await this.$refs.importFormRef.validate()
      if (!valid) return

      this.importLoading = true
      try {
        // 转换中文值为英文枚举值
        const examTypeMap = {
          '物理类': 'PHYSICS',
          '历史类': 'HISTORY'
        }
        const examLevelMap = {
          '校级': 'SCHOOL',
          '市级': 'CITY', 
          '省级': 'PROVINCE'
        }
        
        this.importResult = await api.exams.importStandardTemplate(this.selectedFile, {
          exam_name: this.importForm.exam_name,
          exam_date: this.importForm.exam_date,
          exam_type: examTypeMap[this.importForm.exam_type],
          exam_level: examLevelMap[this.importForm.exam_level],
          subject_combination: this.importForm.subject_combination
        })
        
        this.$message.success('标准模板导入成功!')
      } catch (error) {
        this.$message.error('导入失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.importLoading = false
      }
    },

    resetForm() {
      this.selectedFile = null
      this.importResult = null
      this.$refs.uploadRef.clearFiles()
      this.$refs.importFormRef.resetFields()
    },

    viewExamAnalysis() {
      if (this.importResult?.exam_id) {
        this.$router.push({
          path: '/exam-analysis',
          query: { examId: this.importResult.exam_id }
        })
      }
    }
  }
}
</script>

<style scoped>
.standard-template-import {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.import-result {
  margin-top: 30px;
}

.template-help h3, .template-help h4, .template-help h5 {
  color: #303133;
  margin-top: 20px;
  margin-bottom: 10px;
}

.template-help h3 {
  border-bottom: 2px solid #409EFF;
  padding-bottom: 5px;
}

.subject-info {
  display: flex;
  gap: 30px;
  margin: 15px 0;
}

.subject-group {
  flex: 1;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.subject-group h5 {
  margin-top: 0;
  color: #409EFF;
}

.template-help ul {
  padding-left: 20px;
}

.template-help li {
  margin-bottom: 5px;
}

.column-order-example {
  margin: 15px 0;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.order-example {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}

.step {
  background-color: #409EFF;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.arrow {
  color: #409EFF;
  font-weight: bold;
}

.combination-info {
  margin: 15px 0;
  padding: 15px;
  background-color: #fff7e6;
  border-radius: 4px;
  border-left: 4px solid #E6A23C;
}

.combination-info ul {
  margin: 10px 0;
  padding-left: 20px;
}

.combination-info li {
  margin-bottom: 8px;
}
</style>