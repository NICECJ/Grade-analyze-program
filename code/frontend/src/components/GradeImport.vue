<template>
  <div class="grade-import">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成绩数据导入</span>
        </div>
      </template>

      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="上传文件" />
        <el-step title="字段映射" />
        <el-step title="导入完成" />
      </el-steps>

      <!-- 步骤1: 文件上传 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-alert
          title="成绩导入说明"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        >
          <p>请上传包含学生成绩的Excel文件，支持以下功能：</p>
          <ul>
            <li>支持多科目成绩同时导入（语文、数学、英语、物理、化学、生物、历史、地理、政治、总分）</li>
            <li>自动识别学生信息（姓名、学校、班级）</li>
            <li>支持各科目的排名信息（校排名、市排名、省排名）</li>
          </ul>
        </el-alert>

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
            将成绩Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 .xlsx/.xls 文件
            </div>
          </template>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <p><strong>已选择文件:</strong> {{ selectedFile.name }}</p>
          <el-button type="primary" @click="previewFile" :loading="previewLoading">
            预览文件
          </el-button>
        </div>

        <!-- 预览数据 -->
        <div v-if="previewData" class="preview-section">
          <h3>文件预览</h3>
          <p><strong>检测到的列:</strong></p>
          <div class="column-tags">
            <el-tag 
              v-for="col in previewData.columns" 
              :key="col" 
              class="column-tag"
              :type="getColumnType(col)"
            >
              {{ col }}
            </el-tag>
          </div>
          
          <el-table :data="previewData.sample_data" style="width: 100%; margin-top: 20px" max-height="300">
            <el-table-column
              v-for="col in previewData.columns.slice(0, 8)"
              :key="col"
              :prop="col"
              :label="col"
              width="120"
              show-overflow-tooltip
            />
          </el-table>

          <div class="step-actions">
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </div>
        </div>
      </div>

      <!-- 步骤2: 字段映射 -->
      <div v-if="currentStep === 1" class="step-content">
        <h3>字段映射配置</h3>
        
        <el-form :model="mappingForm" label-width="120px">
          <el-form-item label="考试名称" required>
            <el-input v-model="mappingForm.exam_name" placeholder="请输入考试名称" />
          </el-form-item>
          <el-form-item label="考试日期" required>
            <el-date-picker
              v-model="mappingForm.exam_date"
              type="datetime"
              placeholder="选择考试日期"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
          <el-form-item label="考试类型" required>
            <el-radio-group v-model="mappingForm.exam_type">
              <el-radio label="物理类">物理类</el-radio>
              <el-radio label="历史类">历史类</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="考试级别" required>
            <el-select v-model="mappingForm.exam_level" placeholder="选择考试级别">
              <el-option label="校级考试" value="校级" />
              <el-option label="市级考试" value="市级" />
              <el-option label="省级考试" value="省级" />
            </el-select>
          </el-form-item>
        </el-form>

        <el-divider content-position="left">基本信息映射</el-divider>
        <div class="mapping-section">
          <div class="mapping-item" v-for="field in basicFields" :key="field.key">
            <div class="field-info">
              <strong>{{ field.label }}</strong>
              <span class="field-desc">{{ field.description }}</span>
            </div>
            <el-select
              v-model="fieldMappings[field.key]"
              placeholder="选择Excel列"
              clearable
            >
              <el-option
                v-for="col in previewData.columns"
                :key="col"
                :label="col"
                :value="col"
              />
            </el-select>
          </div>
        </div>

        <el-divider content-position="left">科目成绩映射</el-divider>
        <div class="subject-mapping">
          <div class="subject-item" v-for="subject in subjects" :key="subject.key">
            <h4>{{ subject.label }}</h4>
            <div class="subject-fields">
              <div class="field-row">
                <label>成绩:</label>
                <el-select
                  v-model="fieldMappings[subject.key + '_score']"
                  placeholder="选择成绩列"
                  clearable
                >
                  <el-option
                    v-for="col in previewData.columns"
                    :key="col"
                    :label="col"
                    :value="col"
                  />
                </el-select>
              </div>
              <div class="field-row">
                <label>校排名:</label>
                <el-select
                  v-model="fieldMappings[subject.key + '_rank_school']"
                  placeholder="选择校排名列"
                  clearable
                >
                  <el-option
                    v-for="col in previewData.columns"
                    :key="col"
                    :label="col"
                    :value="col"
                  />
                </el-select>
              </div>
              <div class="field-row">
                <label>市排名:</label>
                <el-select
                  v-model="fieldMappings[subject.key + '_rank_city']"
                  placeholder="选择市排名列"
                  clearable
                >
                  <el-option
                    v-for="col in previewData.columns"
                    :key="col"
                    :label="col"
                    :value="col"
                  />
                </el-select>
              </div>
              <div class="field-row">
                <label>省排名:</label>
                <el-select
                  v-model="fieldMappings[subject.key + '_rank_province']"
                  placeholder="选择省排名列"
                  clearable
                >
                  <el-option
                    v-for="col in previewData.columns"
                    :key="col"
                    :label="col"
                    :value="col"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <el-button @click="prevStep">上一步</el-button>
          <el-button type="primary" @click="importData" :loading="importLoading">
            开始导入
          </el-button>
        </div>
      </div>

      <!-- 步骤3: 导入完成 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="success-content">
          <el-result
            icon="success"
            title="导入成功!"
            :sub-title="`成功导入 ${importResult.imported_records} 条成绩记录`"
          >
            <template #extra>
              <el-button @click="resetForm">重新导入</el-button>
              <el-button type="primary" @click="$router.push('/exam-analysis')">
                查看考试分析
              </el-button>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'GradeImport',
  data() {
    return {
      currentStep: 0,
      selectedFile: null,
      previewData: null,
      previewLoading: false,
      importLoading: false,
      mappingForm: {
        exam_name: '',
        exam_date: '',
        exam_type: '物理类',
        exam_level: '校级'
      },
      fieldMappings: {},
      importResult: null,
      basicFields: [
        { key: 'name', label: '姓名', description: '学生姓名（必填）' },
        { key: 'school', label: '学校', description: '所属学校' },
        { key: 'current_class', label: '班级', description: '所在班级' },
        { key: 'grade_level', label: '年级', description: '年级信息' }
      ],
      subjects: [
        { key: '语文', label: '语文' },
        { key: '数学', label: '数学' },
        { key: '英语', label: '英语' },
        { key: '物理', label: '物理' },
        { key: '化学', label: '化学' },
        { key: '生物', label: '生物' },
        { key: '历史', label: '历史' },
        { key: '地理', label: '地理' },
        { key: '政治', label: '政治' },
        { key: '总分', label: '总分' }
      ]
    }
  },
  methods: {
    handleFileChange(file) {
      this.selectedFile = file.raw
      this.previewData = null
    },

    async previewFile() {
      if (!this.selectedFile) return
      
      this.previewLoading = true
      try {
        this.previewData = await api.exams.previewExcel(this.selectedFile)
        
        // 如果有智能映射建议，应用它们
        if (this.previewData.structure?.suggested_mappings) {
          this.fieldMappings = { ...this.previewData.structure.suggested_mappings }
        }
      } catch (error) {
        this.$message.error('文件预览失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.previewLoading = false
      }
    },

    getColumnType(column) {
      const col = column.toLowerCase()
      if (col.includes('姓名') || col.includes('name')) return 'success'
      if (col.includes('学校') || col.includes('school')) return 'warning'
      if (col.includes('排名') || col.includes('rank')) return 'info'
      if (col.includes('分数') || col.includes('成绩') || col.includes('score')) return 'danger'
      return ''
    },

    async importData() {
      if (!this.mappingForm.exam_name) {
        this.$message.error('请输入考试名称')
        return
      }

      if (!this.mappingForm.exam_date) {
        this.$message.error('请选择考试日期')
        return
      }

      if (!this.mappingForm.exam_type) {
        this.$message.error('请选择考试类型')
        return
      }

      if (!this.mappingForm.exam_level) {
        this.$message.error('请选择考试级别')
        return
      }

      const columnMappings = Object.entries(this.fieldMappings)
        .filter(([key, value]) => value)
        .map(([system_field, excel_column]) => ({
          excel_column,
          system_field
        }))

      if (columnMappings.length === 0) {
        this.$message.error('请至少配置一个字段映射')
        return
      }

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
        
        this.importResult = await api.exams.importGrades(this.selectedFile, {
          exam_name: this.mappingForm.exam_name,
          exam_date: this.mappingForm.exam_date,
          exam_type: examTypeMap[this.mappingForm.exam_type],
          exam_level: examLevelMap[this.mappingForm.exam_level],
          column_mappings: columnMappings
        })
        this.nextStep()
        this.$message.success('成绩数据导入成功!')
      } catch (error) {
        this.$message.error('导入失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.importLoading = false
      }
    },

    nextStep() {
      this.currentStep++
    },

    prevStep() {
      this.currentStep--
    },

    resetForm() {
      this.currentStep = 0
      this.selectedFile = null
      this.previewData = null
      this.mappingForm.exam_name = ''
      this.mappingForm.exam_date = ''
      this.mappingForm.exam_type = '物理类'
      this.mappingForm.exam_level = '校级'
      this.fieldMappings = {}
      this.importResult = null
      this.$refs.uploadRef.clearFiles()
    }
  }
}
</script>

<style scoped>
.grade-import {
  max-width: 1200px;
  margin: 0 auto;
}

.step-content {
  margin-top: 30px;
}

.file-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-section {
  margin-top: 30px;
}

.column-tags {
  margin: 10px 0;
}

.column-tag {
  margin: 5px;
}

.mapping-section {
  margin-top: 20px;
}

.mapping-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.field-info {
  flex: 1;
  margin-right: 20px;
}

.field-desc {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.subject-mapping {
  margin-top: 20px;
}

.subject-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.subject-item h4 {
  margin: 0 0 15px 0;
  color: #409EFF;
}

.subject-fields {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.field-row {
  display: flex;
  align-items: center;
}

.field-row label {
  width: 80px;
  margin-right: 10px;
  font-size: 14px;
}

.step-actions {
  margin-top: 30px;
  text-align: center;
}

.success-content {
  text-align: center;
  padding: 40px;
}
</style>