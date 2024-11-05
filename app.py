import streamlit as st
import cv2
import numpy as np
import os

def analyze_skin_color(image):
    """피부색 분석 함수"""
    # HSV 색공간으로 변환
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 피부색 범위 설정 (HSV)
    lower_skin = np.array([0, 20, 70])
    upper_skin = np.array([20, 255, 255])
    
    # 피부색 마스크 생성
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # 마스크를 이용해 피부 영역만 추출
    skin = cv2.bitwise_and(image, image, mask=mask)
    
    # 피부색이 있는 픽셀만 선택
    skin_pixels = skin[mask > 0]
    
    if len(skin_pixels) == 0:
        return None
    
    # 평균 색상 계산 (BGR에서 RGB로 변환)
    average_color = np.mean(skin_pixels, axis=0).astype(int)
    average_color = average_color[::-1]  # BGR to RGB
    
    return average_color

def get_central_region(image, percentage=60):
    """이미지 중앙 부분 추출"""
    height, width = image.shape[:2]
    
    # 중앙 영역 계산 (percentage%만큼의 영역)
    margin_x = int(width * (100 - percentage) / 200)
    margin_y = int(height * (100 - percentage) / 200)
    
    center_region = image[margin_y:height-margin_y, margin_x:width-margin_x]
    return center_region

def main():
    st.title("얼굴 피부색 분석기")
    st.write("사진을 업로드하면 피부의 평균 색상을 분석해드립니다.")
    
    st.info("💡 팁: 얼굴이 화면의 중앙에 있고, 조명이 적절한 사진을 사용하면 더 정확한 결과를 얻을 수 있습니다.")
    
    uploaded_file = st.file_uploader("얼굴 사진을 선택하세요", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # 이미지 로드 및 처리
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # 이미지가 너무 크면 리사이즈
        max_size = 800
        if max(image.shape) > max_size:
            ratio = max_size / max(image.shape)
            image = cv2.resize(image, None, fx=ratio, fy=ratio)
        
        # 이미지 중앙 부분 추출 (얼굴이 주로 중앙에 있다고 가정)
        center_region = get_central_region(image)
        
        # 결과 표시를 위한 컬럼 생성
        col1, col2 = st.columns(2)
        
        with col1:
            # BGR에서 RGB로 변환하여 표시
            st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="업로드된 사진", use_column_width=True)
        
        with col2:
            # 피부색 분석
            color = analyze_skin_color(center_region)
            
            if color is not None:
                st.success("피부색 분석 완료!")
                st.write(f"RGB 값: {color}")
                
                # 색상 표시
                color_display = np.ones((100, 100, 3), dtype=np.uint8)
                color_display[:] = color
                st.image(color_display, caption=f"추출된 피부색", use_column_width=True)
                
                # HEX 코드 표시
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                st.write(f"HEX 코드: {hex_color}")
                
                # 추가 정보 표시
                st.info("""
                🎨 색상 활용 팁:
                - 메이크업 제품 선택 시 참고할 수 있습니다
                - 의상 컬러 매칭에 활용할 수 있습니다
                - 퍼스널 컬러 진단의 기초 자료로 사용할 수 있습니다
                """)
            else:
                st.error("피부색을 추출할 수 없습니다. 다른 사진을 시도해보세요.")

if __name__ == "__main__":
    main()