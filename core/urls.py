from django.urls import path

from core import views

urlpatterns = [
    path('', views.LandingView.as_view(), name='index'),
    path('cadastro/', views.RegisterView.as_view(), name='register'),
    path('conta-desativada/', views.AccountDisabledView.as_view(), name='account_disabled'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('tarefas/', views.TaskListView.as_view(), name='tasks'),
    path('tarefas/nova/', views.TaskCreateView.as_view(), name='task_create'),
    path('tarefas/<int:pk>/editar/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('tarefas/<int:pk>/excluir/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tarefas/<int:pk>/concluir/', views.TaskCompleteView.as_view(), name='task_complete'),
    path('missoes/', views.DailyTasksView.as_view(), name='daily'),
    path('loja/', views.ShopView.as_view(), name='shop'),
    path('loja/<int:pk>/comprar/', views.BuyItemView.as_view(), name='buy_item'),
    path('inventario/', views.InventoryView.as_view(), name='inventory'),
    path('inventario/<int:pk>/usar/', views.UseItemView.as_view(), name='use_item'),
    path('inventario/<int:pk>/equipar/', views.ToggleEquipView.as_view(), name='toggle_equip'),
    path('amigos/', views.FriendsView.as_view(), name='friends'),
    path('amigos/<int:pk>/aceitar/', views.FriendshipAcceptView.as_view(), name='friend_accept'),
    path('amigos/<int:pk>/recusar/', views.FriendshipRejectView.as_view(), name='friend_reject'),
]
