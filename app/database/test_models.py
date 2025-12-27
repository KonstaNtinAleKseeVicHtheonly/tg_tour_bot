from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

# class TourLandmarkAssociation(Base):
#     """Ассоциативный класс для связи many-to-many с дополнительными данными"""
#     __tablename__ = 'tour_landmark'
    
#     tour_id: Mapped[int] = mapped_column(ForeignKey('tours.id', ondelete='CASCADE'), primary_key=True)
#     landmark_id: Mapped[int] = mapped_column(ForeignKey('landmarks.id', ondelete='CASCADE'), primary_key=True)
    
#     # Дополнительные поля связи
#     order_index: Mapped[int] = mapped_column(default=0)
#     visit_duration: Mapped[int] = mapped_column(default=30, comment='Длительность в минутах')
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
#     # Связи с основными моделями
#     tour: Mapped['Tour'] = relationship(back_populates='landmark_associations')
#     landmark: Mapped['Landmark'] = relationship(back_populates='tour_associations')
    
#     def __repr__(self):
#         return f'<TourLandmark tour={self.tour_id}, landmark={self.landmark_id}, order={self.order_index}>'

# class Landmark(Base):
#     __tablename__ = 'landmarks'
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255))
    
#     # Связь через ассоциативный класс
#     tour_associations: Mapped[list['TourLandmarkAssociation']] = relationship(
#         back_populates='landmark',
#         cascade='all, delete-orphan'
#     )
    
#     # Свойство для быстрого доступа к турам
#     @property
#     def tours(self):
#         return [assoc.tour for assoc in self.tour_associations]

# class Tour(Base):
#     __tablename__ = 'tours'
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255))
    
#     # Связь через ассоциативный класс с сортировкой
#     landmark_associations: Mapped[list['TourLandmarkAssociation']] = relationship(
#         back_populates='tour',
#         cascade='all, delete-orphan',
#         order_by='TourLandmarkAssociation.order_index'
#     )
    
#     # Свойство для быстрого доступа к достопримечательностям
#     @property
#     def landmarks(self):
        # return [assoc.landmark for assoc in self.landmark_associations]
        
        
# from sqlalchemy.orm import Session, joinedload

# class TourLandmarkManager:
#     """Менеджер для работы со связями через ассоциативный класс"""
    
#     def __init__(self, session: Session):
#         self.session = session
    
#     # CREATE
#     def add_landmark_to_tour(self, tour_id: int, landmark_id: int, order_index: int = 0, duration: int = 30):
#         """Добавить достопримечательность в тур"""
#         # Проверяем существование связи
#         existing = self.session.get(TourLandmarkAssociation, (tour_id, landmark_id))
        
#         if existing:
#             existing.order_index = order_index
#             existing.visit_duration = duration
#         else:
#             association = TourLandmarkAssociation(
#                 tour_id=tour_id,
#                 landmark_id=landmark_id,
#                 order_index=order_index,
#                 visit_duration=duration
#             )
#             self.session.add(association)
        
#         self.session.commit()
#         return association
    
#     def bulk_add_landmarks(self, tour_id: int, landmark_data: list[dict]):
#         """Добавить несколько достопримечательностей"""
#         for idx, data in enumerate(landmark_data, 1):
#             self.add_landmark_to_tour(
#                 tour_id=tour_id,
#                 landmark_id=data['landmark_id'],
#                 order_index=data.get('order_index', idx),
#                 duration=data.get('duration', 30)
#             )
    
#     # READ
#     def get_tour_with_landmarks(self, tour_id: int):
#         """Получить тур с достопримечательностями и данными связи"""
#         tour = self.session.get(Tour, tour_id)
#         if not tour:
#             return None
        
#         # Загружаем связи с дополнительными данными
#         associations = (
#             self.session.query(TourLandmarkAssociation)
#             .filter_by(tour_id=tour_id)
#             .order_by(TourLandmarkAssociation.order_index)
#             .all()
#         )
        
#         result = {
#             'id': tour.id,
#             'name': tour.name,
#             'landmarks': []
#         }
        
#         for assoc in associations:
#             result['landmarks'].append({
#                 'landmark_id': assoc.landmark.id,
#                 'landmark_name': assoc.landmark.name,
#                 'order_index': assoc.order_index,
#                 'visit_duration': assoc.visit_duration,
#                 'created_at': assoc.created_at
#             })
        
#         return result
    
#     def get_landmark_tours(self, landmark_id: int):
#         """Получить все туры с этой достопримечательностью"""
#         associations = (
#             self.session.query(TourLandmarkAssociation)
#             .filter_by(landmark_id=landmark_id)
#             .order_by(TourLandmarkAssociation.created_at)
#             .all()
#         )
        
#         return [assoc.tour for assoc in associations]
    
#     # UPDATE
#     def update_association(self, tour_id: int, landmark_id: int, **kwargs):
#         """Обновить данные связи"""
#         association = self.session.get(TourLandmarkAssociation, (tour_id, landmark_id))
#         if not association:
#             return False
        
#         for key, value in kwargs.items():
#             if hasattr(association, key):
#                 setattr(association, key, value)
        
#         self.session.commit()
#         return True
    
#     def reorder_landmarks(self, tour_id: int, new_order: list[int]):
#         """Изменить порядок достопримечательностей"""
#         for order_index, landmark_id in enumerate(new_order, 1):
#             self.update_association(tour_id, landmark_id, order_index=order_index)
    
#     # DELETE
#     def remove_landmark_from_tour(self, tour_id: int, landmark_id: int):
#         """Удалить достопримечательность из тура"""
#         association = self.session.get(TourLandmarkAssociation, (tour_id, landmark_id))
#         if association:
#             self.session.delete(association)
#             self.session.commit()
#             return True
#         return False
    
#     def clear_tour_landmarks(self, tour_id: int):
#         """Очистить все достопримечательности из тура"""
#         self.session.query(TourLandmarkAssociation).filter_by(tour_id=tour_id).delete()
#         self.session.commit()